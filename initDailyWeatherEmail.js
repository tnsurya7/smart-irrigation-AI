/**
 * Daily Weather Email Service Initializer
 * Import this file in your main application to start the daily weather email service
 * This module is completely independent and won't affect existing functionality
 */

const DailyWeatherEmailService = require('./dailyWeatherEmail.service.js');

// Initialize the daily weather email service
let weatherEmailService = null;

function initializeDailyWeatherEmail() {
    try {
        console.log('🌱 Initializing Daily Weather Email Automation...');
        
        weatherEmailService = new DailyWeatherEmailService();
        weatherEmailService.initialize();
        
        console.log('✅ Daily Weather Email Automation initialized successfully');
        return weatherEmailService;
    } catch (error) {
        console.error('❌ Failed to initialize Daily Weather Email Service:', error.message);
        console.error('⚠️ Main application will continue without daily weather emails');
        return null;
    }
}

// Auto-initialize when this module is required
const service = initializeDailyWeatherEmail();

module.exports = {
    service,
    initializeDailyWeatherEmail
};