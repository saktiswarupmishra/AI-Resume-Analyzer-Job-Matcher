const express = require('express');
const { PrismaClient } = require('@prisma/client');
const authMiddleware = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

// GET /api/analysis/:resumeId
router.get('/:resumeId', authMiddleware, async (req, res) => {
  try {
    const resumeId = parseInt(req.params.resumeId);

    const resume = await prisma.resume.findFirst({
      where: { id: resumeId, userId: req.user.id },
      include: {
        analysisResult: true,
        skills: true,
      },
    });

    if (!resume) return res.status(404).json({ error: 'Resume not found.' });
    if (!resume.analysisResult) {
      return res.json({
        status: resume.status,
        message: resume.status === 'parsing' ? 'Analysis in progress...' : 'No analysis available.',
      });
    }

    res.json({
      status: 'analyzed',
      analysis: resume.analysisResult,
      skills: resume.skills,
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch analysis.' });
  }
});

// GET /api/analysis/jobs/:resumeId
router.get('/jobs/:resumeId', authMiddleware, async (req, res) => {
  try {
    const resumeId = parseInt(req.params.resumeId);

    const resume = await prisma.resume.findFirst({
      where: { id: resumeId, userId: req.user.id },
    });

    if (!resume) return res.status(404).json({ error: 'Resume not found.' });

    const jobMatches = await prisma.jobMatch.findMany({
      where: { resumeId },
      orderBy: { matchScore: 'desc' },
    });

    res.json({ jobMatches });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch job matches.' });
  }
});

module.exports = router;
