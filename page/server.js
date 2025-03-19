const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse form data
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, '../public')));

// Route to serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// GET request for harvest.html
app.get('/harvest', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/harvest.html'));
});

// POST request to redirect to harvest.html
app.post('/harvest', (req, res) => {
    res.redirect('/harvest');
});
app.get('/soiltesting', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'soiltesting.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

