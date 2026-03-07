import axios from 'axios';
import { logger } from '@config/logger.js';

const BREVO_API_KEY = process.env.BREVO_API_KEY || '';
const BREVO_SENDER_EMAIL = process.env.BREVO_SENDER_EMAIL || 'noreply@nexar.com';
const BREVO_SENDER_NAME = process.env.BREVO_SENDER_NAME || 'Nexar';
const API_URL = (process.env.API_URL || 'http://localhost:3000') + '/api/v1/auth';

logger.debug("Email service initialized", {
  senderEmail: BREVO_SENDER_EMAIL,
  senderName: BREVO_SENDER_NAME,
  apiUrl: API_URL,
  brevoKeyConfigured: !!BREVO_API_KEY,
});

const brevoClient = axios.create({
  baseURL: 'https://api.brevo.com/v3',
  headers: {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json',
  },
});

export async function sendVerificationEmail(
  to: string,
  name: string,
  verificationToken: string
): Promise<void> {
  const verificationUrl = `${API_URL}/verify-email?token=${verificationToken}`;

  logger.debug("Preparing verification email", {
    to,
    name,
    verificationUrlLength: verificationUrl.length,
    sender: `${BREVO_SENDER_NAME} <${BREVO_SENDER_EMAIL}>`,
  });

  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f172a;padding:40px 20px;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background-color:#1e293b;border-radius:12px;overflow:hidden;">
              <!-- Header -->
              <tr>
                <td style="padding:32px 40px;background:linear-gradient(135deg,#1e293b,#334155);border-bottom:1px solid #334155;">
                  <h1 style="margin:0;font-size:24px;font-weight:700;color:#f8fafc;font-family:monospace;">Nexar</h1>
                  <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">Quantum-Classical Code Router</p>
                </td>
              </tr>
              <!-- Body -->
              <tr>
                <td style="padding:40px;">
                  <h2 style="margin:0 0 16px;font-size:20px;color:#f1f5f9;">Verify your email address</h2>
                  <p style="margin:0 0 24px;font-size:15px;color:#cbd5e1;line-height:1.6;">
                    Hi ${name},<br><br>
                    Thanks for creating a Nexar account. Please verify your email address by clicking the button below.
                  </p>
                  <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
                    <tr>
                      <td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:8px;padding:14px 32px;">
                        <a href="${verificationUrl}" style="color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;display:inline-block;">
                          Verify Email Address
                        </a>
                      </td>
                    </tr>
                  </table>
                  <p style="margin:0 0 8px;font-size:13px;color:#94a3b8;">Or copy and paste this link into your browser:</p>
                  <p style="margin:0 0 24px;font-size:13px;color:#6366f1;word-break:break-all;">${verificationUrl}</p>
                  <p style="margin:0;font-size:13px;color:#64748b;line-height:1.5;">
                    This link expires in 24 hours. If you didn't create an account, you can safely ignore this email.
                  </p>
                </td>
              </tr>
              <!-- Footer -->
              <tr>
                <td style="padding:24px 40px;border-top:1px solid #334155;">
                  <p style="margin:0;font-size:12px;color:#475569;text-align:center;">
                    &copy; ${new Date().getFullYear()} Nexar. All rights reserved.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
  `;

  logger.debug("Sending verification email via Brevo API", {
    to,
    subject: "Verify your email - Nexar",
    htmlContentLength: htmlContent.length,
  });

  const startTime = Date.now();

  try {
    const response = await brevoClient.post('/smtp/email', {
      sender: { name: BREVO_SENDER_NAME, email: BREVO_SENDER_EMAIL },
      to: [{ email: to, name }],
      subject: 'Verify your email - Nexar',
      htmlContent,
    });

    const durationMs = Date.now() - startTime;

    logger.info("Verification email sent successfully", {
      to,
      durationMs,
      brevoStatusCode: response.status,
    });

    logger.debug("Brevo API response details", {
      to,
      statusCode: response.status,
      durationMs,
      responseMessageId: response.data?.messageId,
    });
  } catch (error: any) {
    const durationMs = Date.now() - startTime;

    // Extract Brevo-specific error details if available
    const brevoStatus = error.response?.status;
    const brevoError = error.response?.data;

    if (brevoStatus) {
      logger.warn("Brevo API returned error status", {
        to,
        brevoStatusCode: brevoStatus,
        brevoError: typeof brevoError === 'object' ? JSON.stringify(brevoError).substring(0, 500) : String(brevoError),
        durationMs,
      });
    }

    logger.error('Failed to send verification email via Brevo', {
      to,
      errorMessage: error.message,
      errorCode: error.code,
      brevoStatusCode: brevoStatus,
      durationMs,
    });

    throw new Error('Failed to send verification email');
  }
}
