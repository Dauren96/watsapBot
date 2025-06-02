
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const mongoose = require('mongoose');

require('dotenv').config();

mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('🟢 MongoDB connected'))
  .catch(err => console.error('🔴 MongoDB error:', err));

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
    console.log('📸 Открой QR-код по ссылке: https://api.qrserver.com/v1/create-qr-code/?data=' + encodeURIComponent(qr));
});

client.on('ready', () => {
    console.log('✅ Бот подключен!');
});

client.on('message', async msg => {
    if (msg.body.toLowerCase() === 'hi' || msg.body.toLowerCase() === 'hello') {
        msg.reply('👋 Привет! Я активен.');
    }
});

client.initialize();
