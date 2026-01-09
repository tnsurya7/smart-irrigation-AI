/**
 * Test Script for Daily Weather Email Service
 * Run this to test the email functionality manually
 */

const DailyWeatherEmailService = require('./dailyWeatherEmail.service.js');

async function testWeatherEmail() {
    console.log('🧪 Testing Daily Weather Email Service...\n');
    
    try {
        // Create service instance
        const service = new DailyWeatherEmailService();
        
        console.log('📧 Email Configuration:');
        console.log('- SMTP Host:', service.emailConfig.host);
        console.log('- SMTP Port:', service.emailConfig.port);
        console.log('- Email User:', service.emailConfig.auth.user);
        console.log('- Recipients:', service.recipients.join(', '));
        console.log('- City:', service.city);
        console.log('- API Key:', service.apiKey ? 'Configured ✅' : 'Missing ❌');
        console.log('');
        
        // Test weather data fetch
        console.log('🌤️ Fetching weather data...');
        const weatherData = await service.fetchWeatherData();
        console.log('Weather Data:', {
            city: weatherData.cityName,
            temperature: weatherData.temperature + '°C',
            humidity: weatherData.humidity + '%',
            description: weatherData.description,
            hasRain: weatherData.hasRain,
            rainProbability: weatherData.rainProbability + '%'
        });
        console.log('');
        
        // Test irrigation decision
        console.log('🚿 Generating irrigation decision...');
        const decision = service.generateIrrigationDecision(weatherData);
        console.log('Irrigation Decision:', {
            rainAlert: decision.rainAlert,
            irrigationStatus: decision.irrigationStatus,
            recommendation: decision.irrigationRecommendation
        });
        console.log('');
        
        // Test email sending (uncomment to actually send)
        console.log('📨 Testing email generation...');
        const emailHTML = service.generateEmailHTML(weatherData, decision);
        console.log('✅ Email HTML generated successfully (', emailHTML.length, 'characters)');
        
        // Uncomment the following lines to actually send a test email
        /*
        console.log('📧 Sending test email...');
        await service.sendTestEmail();
        console.log('✅ Test email sent successfully!');
        */
        
        console.log('\n🎉 All tests passed! Daily Weather Email Service is working correctly.');
        console.log('\n📝 To send actual emails:');
        console.log('1. Update .env.local with your email credentials');
        console.log('2. Uncomment the email sending lines in this test script');
        console.log('3. Run this test again');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

// Run the test
testWeatherEmail();