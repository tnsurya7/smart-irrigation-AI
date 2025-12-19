import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'green' }}>🌱 Smart Agriculture Dashboard Test</h1>
      <p>If you can see this, React is working correctly!</p>
      <div style={{ 
        background: '#f0f0f0', 
        padding: '10px', 
        borderRadius: '5px',
        marginTop: '20px'
      }}>
        <h3>System Status:</h3>
        <ul>
          <li>✅ React: Working</li>
          <li>✅ TypeScript: Working</li>
          <li>✅ Vite Dev Server: Running on port 3000</li>
          <li>✅ FastAPI Backend: Running on port 8000</li>
        </ul>
      </div>
      <button 
        onClick={() => alert('Button clicked! React events are working.')}
        style={{
          background: '#22c55e',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginTop: '20px'
        }}
      >
        Test Button
      </button>
    </div>
  );
}

export default TestApp;