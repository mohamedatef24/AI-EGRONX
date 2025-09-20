# AI-EGRONX Chatbot Demo

A beautiful, modern web interface for the AI-EGRONX RAG-powered chatbot.

## Features

- 🎨 **Modern Design**: Clean, responsive interface with gradient backgrounds and smooth animations
- 💬 **Real-time Chat**: Interactive chat interface with typing indicators
- 🤖 **AI Integration**: Powered by Cohere AI and vector search
- 📱 **Mobile Responsive**: Works perfectly on desktop and mobile devices
- ⚡ **Fast & Smooth**: Optimized for performance with smooth animations

## Quick Start

1. **Start the API Server**:
   ```bash
   cd src
   uvicorn main:app --reload --host 0.0.0.0
   ```

2. **Open the Demo**:
   - Open `demo/index.html` in your web browser
   - Or serve it with a local server:
     ```bash
     cd demo
     python -m http.server 8001
     # Then visit http://localhost:8001
     ```

3. **Test the Chatbot**:
   - Ask questions like "What is the college vision?"
   - Try "What is the AI program about?"
   - Ask about academic education or research fields

## Demo Screenshots

The demo includes:
- **Header**: Project branding with gradient background
- **Status Bar**: Real-time system status indicators
- **Chat Area**: Interactive conversation interface
- **Sample Questions**: Quick-start question buttons
- **Input Area**: Clean input field with send button

## API Endpoints Used

- `GET /` - Welcome message
- `POST /nlp/index/answer/1` - Get AI-generated answers

## Customization

### Colors
The demo uses a purple/blue gradient theme. To change colors, modify the CSS variables in the `<style>` section:

```css
/* Main gradient */
background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);

/* Accent colors */
--primary-color: #4f46e5;
--secondary-color: #7c3aed;
```

### API Configuration
To change the API endpoint, modify the `API_BASE` variable in the JavaScript:

```javascript
const API_BASE = 'http://localhost:8000'; // Change this to your API URL
```

### Sample Questions
Add or modify sample questions in the HTML:

```html
<div class="sample-question" onclick="askSampleQuestion('Your question here')">
    Your question here
</div>
```

## Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## Troubleshooting

### API Not Responding
- Make sure the server is running on `http://localhost:8000`
- Check the browser console for error messages
- Verify the API endpoints are working with Postman

### CORS Issues
If you encounter CORS errors, add this to your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## License

This demo is part of the AI-EGRONX project.
