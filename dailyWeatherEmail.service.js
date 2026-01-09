/**
 * Daily Weather Email Automation Service
 * Standalone module for sending daily weather reports via email
 * Does not modify any existing Smart Agriculture functionality
 */

const cron = require('node-cron');
const nodemailer = require('nodemailer');
const axios = require('axios');

// Load environment variables from .env file for local development
try {
    require('dotenv').config();
} catch (error) {
    // dotenv not available, use environment variables directly
}

class DailyWeatherEmailService {
    constructor() {
        this.apiKey = process.env.OPENWEATHER_API_KEY;
        this.city = "Erode,Tamil Nadu,IN";
        this.emailConfig = {
            host: process.env.SMTP_HOST || 'smtp.gmail.com',
            port: process.env.SMTP_PORT || 587,
            secure: false,
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_PASS
            }
        };
        this.recipients = process.env.EMAIL_RECIPIENTS ? 
            process.env.EMAIL_RECIPIENTS.split(',') : 
            [];
        
        // Validate required environment variables
        if (!this.apiKey || !this.emailConfig.auth.user || !this.emailConfig.auth.pass || this.recipients.length === 0) {
            console.error('❌ Daily Weather Email Service: Missing required environment variables');
            console.error('Required: OPENWEATHER_API_KEY, EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENTS');
            return;
        }
        
        this.transporter = null;
        this.initializeEmailTransporter();
    }

    initializeEmailTransporter() {
        try {
            this.transporter = nodemailer.createTransport(this.emailConfig);
            console.log('📧 Daily Weather Email Service: Email transporter initialized');
        } catch (error) {
            console.error('❌ Daily Weather Email Service: Failed to initialize email transporter:', error.message);
        }
    }

    async fetchWeatherData() {
        try {
            const url = `http://api.openweathermap.org/data/2.5/weather?q=${this.city}&appid=${this.apiKey}&units=metric`;
            const forecastUrl = `http://api.openweathermap.org/data/2.5/forecast?q=${this.city}&appid=${this.apiKey}&units=metric`;
            
            const [currentResponse, forecastResponse] = await Promise.all([
                axios.get(url, { timeout: 10000 }),
                axios.get(forecastUrl, { timeout: 10000 })
            ]);

            const current = currentResponse.data;
            const forecast = forecastResponse.data;

            // Calculate rain probability from forecast
            let rainProbability = 0;
            let hasRain = false;
            
            if (forecast.list && forecast.list.length > 0) {
                // Check next 8 forecasts (24 hours)
                const todayForecasts = forecast.list.slice(0, 8);
                const rainForecasts = todayForecasts.filter(f => 
                    f.weather[0].main.toLowerCase().includes('rain') || 
                    (f.rain && f.rain['3h'] > 0)
                );
                rainProbability = Math.round((rainForecasts.length / todayForecasts.length) * 100);
                hasRain = rainForecasts.length > 0;
            }

            return {
                temperature: Math.round(current.main.temp),
                humidity: current.main.humidity,
                description: current.weather[0].description,
                icon: current.weather[0].icon,
                hasRain: hasRain || current.weather[0].main.toLowerCase().includes('rain'),
                rainProbability: rainProbability,
                cityName: current.name,
                country: current.sys.country
            };
        } catch (error) {
            console.error('❌ Daily Weather Email Service: Failed to fetch weather data:', error.message);
            throw error;
        }
    }

    generateIrrigationDecision(weatherData) {
        const { rainProbability, humidity, hasRain } = weatherData;
        
        // Rain Alert Logic
        const rainAlert = rainProbability > 50 || hasRain;
        
        // Irrigation Decision Logic
        let irrigationRecommendation;
        let irrigationStatus;
        
        if (rainAlert) {
            irrigationRecommendation = "Not recommended - Rain expected";
            irrigationStatus = "No";
        } else if (rainProbability <= 30 && humidity < 70) {
            irrigationRecommendation = "Good for irrigation";
            irrigationStatus = "Yes";
        } else {
            irrigationRecommendation = "Not recommended - High humidity or rain chance";
            irrigationStatus = "No";
        }

        return {
            rainAlert,
            irrigationRecommendation,
            irrigationStatus
        };
    }

    generateEmailHTML(weatherData, decision, timeOfDay = 'morning') {
        const { temperature, humidity, description, icon, hasRain, rainProbability, cityName } = weatherData;
        const { rainAlert, irrigationRecommendation, irrigationStatus } = decision;
        
        const weatherIconUrl = `https://openweathermap.org/img/wn/${icon}@2x.png`;
        const currentDate = new Date().toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const currentTime = new Date().toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        // Different greetings based on time of day
        let greeting, reportTitle;
        if (timeOfDay === 'morning') {
            greeting = "Good Morning ☀️<br>Have a nice day and a successful farming day ahead.";
            reportTitle = "🌅 Morning Weather Report";
        } else {
            greeting = "Good Evening 🌅<br>Here's your evening weather update for tomorrow's planning.";
            reportTitle = "🌆 Evening Weather Report";
        }

        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Weather Report - Smart Agriculture</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                    padding: 20px;
                }
                
                .email-container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                
                .header {
                    background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }
                
                .header h1 {
                    font-size: 28px;
                    margin-bottom: 10px;
                    font-weight: 600;
                }
                
                .header .date {
                    font-size: 16px;
                    opacity: 0.9;
                }
                
                .greeting {
                    background: linear-gradient(135deg, #81c784 0%, #66bb6a 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: 500;
                }
                
                .content {
                    padding: 30px 20px;
                }
                
                .weather-card {
                    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-left: 5px solid #4caf50;
                }
                
                .weather-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                
                .weather-location {
                    font-size: 20px;
                    font-weight: 600;
                    color: #2e7d32;
                }
                
                .weather-icon {
                    width: 60px;
                    height: 60px;
                }
                
                .weather-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .weather-item {
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }
                
                .weather-item .label {
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    font-weight: 600;
                    margin-bottom: 5px;
                }
                
                .weather-item .value {
                    font-size: 24px;
                    font-weight: 700;
                    color: #2e7d32;
                }
                
                .weather-item .unit {
                    font-size: 14px;
                    color: #666;
                }
                
                .irrigation-section {
                    background: ${irrigationStatus === 'Yes' ? 'linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)' : 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)'};
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-left: 5px solid ${irrigationStatus === 'Yes' ? '#4caf50' : '#ff9800'};
                }
                
                .irrigation-question {
                    font-size: 18px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 15px;
                }
                
                .irrigation-answer {
                    font-size: 24px;
                    font-weight: 700;
                    color: ${irrigationStatus === 'Yes' ? '#2e7d32' : '#f57c00'};
                    margin-bottom: 10px;
                }
                
                .irrigation-reason {
                    font-size: 14px;
                    color: #666;
                    font-style: italic;
                }
                
                ${rainAlert ? `
                .rain-alert {
                    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                    border: 2px solid #f44336;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 25px;
                    text-align: center;
                }
                
                .rain-alert .alert-icon {
                    font-size: 30px;
                    margin-bottom: 10px;
                }
                
                .rain-alert .alert-text {
                    font-size: 16px;
                    font-weight: 600;
                    color: #c62828;
                }
                ` : ''}
                
                .footer {
                    background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                }
                
                .footer .system-name {
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 5px;
                }
                
                .footer .location {
                    font-size: 14px;
                    opacity: 0.9;
                }
                
                @media (max-width: 600px) {
                    .weather-header {
                        flex-direction: column;
                        text-align: center;
                    }
                    
                    .weather-details {
                        grid-template-columns: 1fr;
                    }
                    
                    .header h1 {
                        font-size: 24px;
                    }
                    
                    .greeting {
                        font-size: 16px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌱 ${reportTitle}</h1>
                    <div class="date">${currentDate} - ${currentTime}</div>
                </div>
                
                <div class="greeting">
                    ${greeting}
                </div>
                
                <div class="content">
                    <div class="weather-card">
                        <div class="weather-header">
                            <div class="weather-location">📍 ${cityName}</div>
                            <img src="${weatherIconUrl}" alt="${description}" class="weather-icon">
                        </div>
                        
                        <div class="weather-details">
                            <div class="weather-item">
                                <div class="label">Temperature</div>
                                <div class="value">${temperature}<span class="unit">°C</span></div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Humidity</div>
                                <div class="value">${humidity}<span class="unit">%</span></div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Condition</div>
                                <div class="value" style="font-size: 16px; text-transform: capitalize;">${description}</div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Rain Chance</div>
                                <div class="value">${rainProbability}<span class="unit">%</span></div>
                            </div>
                        </div>
                    </div>
                    
                    ${rainAlert ? `
                    <div class="rain-alert">
                        <div class="alert-icon">⚠️</div>
                        <div class="alert-text">Rain expected today in Erode. Please avoid irrigation.</div>
                    </div>
                    ` : ''}
                    
                    <div class="irrigation-section">
                        <div class="irrigation-question">🚿 Is today good for irrigation?</div>
                        <div class="irrigation-answer">${irrigationStatus}</div>
                        <div class="irrigation-reason">${irrigationRecommendation}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="system-name">Smart Agriculture System</div>
                    <div class="location">Location: Erode, Tamil Nadu</div>
                </div>
            </div>
        </body>
        </html>
        `;
    }

    async sendDailyWeatherEmail(timeOfDay = 'morning') {
        try {
            console.log(`🌤️ Daily Weather Email Service: Starting ${timeOfDay} weather email process...`);
            
            // Fetch weather data
            const weatherData = await this.fetchWeatherData();
            console.log('✅ Weather data fetched successfully for', weatherData.cityName);
            
            // Generate irrigation decision
            const decision = this.generateIrrigationDecision(weatherData);
            
            // Generate email HTML
            const emailHTML = this.generateEmailHTML(weatherData, decision, timeOfDay);
            
            // Prepare email options
            const reportType = timeOfDay === 'morning' ? 'Morning' : 'Evening';
            const mailOptions = {
                from: `"Smart Agriculture System" <${this.emailConfig.auth.user}>`,
                to: this.recipients.join(','),
                subject: `🌱 ${reportType} Weather Report - ${weatherData.cityName} | ${new Date().toLocaleDateString('en-IN')}`,
                html: emailHTML
            };
            
            // Send email
            if (this.transporter) {
                const info = await this.transporter.sendMail(mailOptions);
                console.log(`✅ ${reportType} weather email sent successfully:`, info.messageId);
                console.log('📧 Recipients:', this.recipients.join(', '));
                console.log('🌡️ Temperature:', weatherData.temperature + '°C');
                console.log('💧 Humidity:', weatherData.humidity + '%');
                console.log('🌧️ Rain Probability:', weatherData.rainProbability + '%');
                console.log('🚿 Irrigation Recommended:', decision.irrigationStatus);
            } else {
                console.error('❌ Email transporter not available');
            }
            
        } catch (error) {
            console.error(`❌ Daily Weather Email Service: Failed to send ${timeOfDay} weather email:`, error.message);
            // Don't throw error to prevent affecting main application
        }
    }

    startDailyCronJob() {
        // Schedule daily emails at 6:00 AM and 7:00 PM IST
        console.log('⏰ Daily Weather Email Service: Scheduling daily emails at 6:00 AM and 7:00 PM IST');
        
        // Morning email at 6:00 AM IST (12:30 AM UTC - IST is UTC+5:30)
        cron.schedule('30 0 * * *', async () => {
            console.log('🌅 Daily Weather Email Service: Executing scheduled morning weather email...');
            await this.sendDailyWeatherEmail('morning');
        }, {
            scheduled: true,
            timezone: "Asia/Kolkata"
        });
        
        // Evening email at 7:00 PM IST (1:30 PM UTC)
        cron.schedule('30 13 * * *', async () => {
            console.log('🌆 Daily Weather Email Service: Executing scheduled evening weather email...');
            await this.sendDailyWeatherEmail('evening');
        }, {
            scheduled: true,
            timezone: "Asia/Kolkata"
        });
        
        console.log('✅ Daily Weather Email Service: Morning and Evening cron jobs scheduled successfully');
    }

    // Method for manual testing
    async sendTestEmail(timeOfDay = 'morning') {
        console.log(`🧪 Daily Weather Email Service: Sending test ${timeOfDay} email...`);
        await this.sendDailyWeatherEmail(timeOfDay);
    }

    // Initialize the service
    initialize() {
        try {
            console.log('🚀 Daily Weather Email Service: Initializing...');
            this.startDailyCronJob();
            console.log('✅ Daily Weather Email Service: Initialized successfully');
            console.log('📧 Email service configured via environment variables');
            console.log('⏰ Schedule: 6:00 AM and 7:00 PM IST daily');
            
            // Send a test email on startup (optional - remove in production)
            // setTimeout(() => this.sendTestEmail('morning'), 5000);
            
        } catch (error) {
            console.error('❌ Daily Weather Email Service: Initialization failed:', error.message);
        }
    }
}

module.exports = DailyWeatherEmailService;