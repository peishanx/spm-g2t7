import dotenv from '@dotenvx/dotenvx';
import nodemailer from 'nodemailer';

dotenv.config();

export const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST, // Use your custom SMTP host
    port: process.env.SMTP_PORT, // Use your custom SMTP port
    secure: false,               // Set to true if using 465, false for 587
    auth: {
      user: process.env.SMTP_USER,        // Use SMTP_USER to align with .env and docker-compose.yaml
      pass: process.env.SMTP_PASS         // Use SMTP_PASS to align with .env and docker-compose.yaml
    },
    tls: {
      rejectUnauthorized: false // Helps if there are TLS certificate issues
    }
});
