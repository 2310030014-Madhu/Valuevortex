import express from 'express';
import mongoose from 'mongoose';
import authRoutes from './routes/auth.js';
import { spawn } from 'child_process';
import cors  from 'cors';


const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());
mongoose.connect('mongodb://localhost:27017/valuevortex')

app.use('/api/auth', authRoutes)

app.get('/search', (req, res) => {
  console.log("Inside the search route");
  const product = req.query.query;
  console.log("Product:", product);
  if (!product) return res.status(400).json({ error: 'Product is required' });

  const python = spawn('python', ['scraper.py', product]);

  let dataBuffer = '';``
  let errorBuffer = '';
  
  python.stdout.on('data', (data) => {
    dataBuffer += data.toString();
  });

  python.stderr.on('data', (data) => {
    errorBuffer += data.toString();
  });

  python.on('close', (code) => {
    if (errorBuffer) {
      console.error('Python error:', errorBuffer);
      return res.status(500).json({ error: 'Error from Python script' });
    }

    try {
      const results = JSON.parse(dataBuffer);
      res.json(results);
    } catch (e) {
      console.error('Failed to parse Python output', e);
      res.status(500).json({ error: 'Invalid output from Python script' });
    }
  });
});



app.listen(PORT, () => {
  console.log(`✅ Server is running at http://localhost:${PORT}`);
});
