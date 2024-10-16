import dotenv from '@dotenvx/dotenvx';
import nodemailer from 'nodemailer';

dotenv.config();

export const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST, // Use your custom SMTP host
    port: process.env.SMTP_PORT, // Use your custom SMTP port
    auth: {
      user: process.env.email,        // Your allinone.com.sg email address
      pass: process.env.email_password // Your allinone.com.sg email password
    },
  });
