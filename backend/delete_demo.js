const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function run() {
  const deleted = await prisma.user.deleteMany({
    where: {
      email: {
        in: ['john@example.com', 'jane@example.com', 'admin@example.com']
      }
    }
  });
  console.log('Deleted', deleted.count, 'demo users');
  await prisma.$disconnect();
}

run().catch(e => { console.error(e); process.exit(1); });
