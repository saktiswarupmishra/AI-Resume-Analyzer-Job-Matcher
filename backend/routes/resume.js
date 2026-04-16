const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const { PrismaClient } = require('@prisma/client');
const authMiddleware = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

// Multer config — local file storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const dir = path.join(__dirname, '..', 'uploads');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1e9)}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    const allowed = ['.pdf', '.docx'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Only PDF and DOCX files are allowed.'));
    }
  },
});

// POST /api/resume/upload
router.post('/upload', authMiddleware, upload.single('resume'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded.' });
    }

    const fileUrl = `${req.protocol}://${req.get('host')}/uploads/${req.file.filename}`;
    const filePath = req.file.path;

    // Save resume record
    const resume = await prisma.resume.create({
      data: {
        userId: req.user.id,
        fileName: req.file.originalname,
        fileUrl,
        fileType: path.extname(req.file.originalname).replace('.', ''),
        status: 'parsing',
      },
    });

    // Send to AI service for analysis (async — don't block response)
    processResume(resume.id, filePath, fileUrl).catch((err) => {
      console.error('AI processing error:', err.message);
    });

    res.status(201).json({
      message: 'Resume uploaded successfully. Analysis in progress.',
      resume: {
        id: resume.id,
        fileName: resume.fileName,
        status: resume.status,
        createdAt: resume.createdAt,
      },
    });
  } catch (err) {
    console.error('Upload error:', err);
    res.status(500).json({ error: 'Upload failed.' });
  }
});

// Background AI processing
async function processResume(resumeId, filePath, fileUrl) {
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';

  try {
    // Send file to AI service
    const formData = new (require('form-data'))();
    const fileStream = fs.createReadStream(filePath);
    formData.append('file', fileStream);

    const response = await axios.post(`${aiUrl}/analyze-resume`, formData, {
      headers: { ...formData.getHeaders() },
      timeout: 120000, // 2 minutes
    });

    const data = response.data;

    // Save raw text
    await prisma.resume.update({
      where: { id: resumeId },
      data: { rawText: data.raw_text || '', status: 'analyzed' },
    });

    // Save analysis result
    await prisma.analysisResult.create({
      data: {
        resumeId,
        atsScore: data.ats_score || 0,
        scoreBreakdown: data.score_breakdown || {},
        sections: data.sections || {},
        suggestions: data.suggestions || [],
        summary: data.summary || '',
        experienceYears: data.experience_years || 0,
        educationLevel: data.education_level || '',
      },
    });

    // Save skills
    if (data.skills && data.skills.length > 0) {
      await prisma.skill.createMany({
        data: data.skills.map((s) => ({
          resumeId,
          name: s.name,
          category: s.category || 'technical',
          level: s.level || 'intermediate',
        })),
      });
    }

    // Save job matches
    if (data.job_matches && data.job_matches.length > 0) {
      await prisma.jobMatch.createMany({
        data: data.job_matches.map((j) => ({
          resumeId,
          jobTitle: j.title,
          company: j.company,
          location: j.location || '',
          description: j.description || '',
          requiredSkills: j.required_skills || [],
          matchScore: j.match_score || 0,
          matchReason: j.match_reason || '',
          jobUrl: j.url || '',
        })),
      });
    }

    console.log(`✅ Resume #${resumeId} analyzed successfully`);
  } catch (err) {
    console.error(`❌ AI analysis failed for resume #${resumeId}:`, err.message);
    await prisma.resume.update({
      where: { id: resumeId },
      data: { status: 'failed' },
    });
  }
}

// GET /api/resume/list
router.get('/list', authMiddleware, async (req, res) => {
  try {
    const resumes = await prisma.resume.findMany({
      where: { userId: req.user.id },
      include: {
        analysisResult: { select: { atsScore: true } },
        _count: { select: { skills: true, jobMatches: true } },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json({ resumes });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch resumes.' });
  }
});

// GET /api/resume/:id
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const resume = await prisma.resume.findFirst({
      where: { id: parseInt(req.params.id), userId: req.user.id },
      include: {
        analysisResult: true,
        skills: true,
        jobMatches: { orderBy: { matchScore: 'desc' } },
      },
    });

    if (!resume) return res.status(404).json({ error: 'Resume not found.' });
    res.json({ resume });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch resume.' });
  }
});

// DELETE /api/resume/:id
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const resume = await prisma.resume.findFirst({
      where: { id: parseInt(req.params.id), userId: req.user.id },
    });

    if (!resume) return res.status(404).json({ error: 'Resume not found.' });

    // Delete local file if exists
    const filename = resume.fileUrl.split('/uploads/')[1];
    if (filename) {
      const filePath = path.join(__dirname, '..', 'uploads', filename);
      if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    }

    await prisma.resume.delete({ where: { id: resume.id } });
    res.json({ message: 'Resume deleted successfully.' });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete resume.' });
  }
});

module.exports = router;
