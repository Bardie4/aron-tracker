// src/App.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Switch, Typography, CircularProgress } from '@mui/material';

interface Metrics {
  total_today: number;
  n_feeds_today: number;
  largest_meal: number;
  last_meal_time: string;
  n_pee_today: number;
  n_poo_today: number;
  suggested_meal: number;
}

function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get<Metrics>('http://localhost:8080/fetch_stats')
      .then(response => {
        setMetrics(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching metrics:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Container style={{ backgroundColor: darkMode ? '#343a40' : '#f8f9fa', color: darkMode ? '#f8f9fa' : '#212529', minHeight: '100vh' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h2">👩‍🍼 Aron tracker</Typography>
        <Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />
      </div>
      <Typography variant="h6">Total Today: {metrics?.total_today} ml</Typography>
      <Typography variant="h6">Meals Today: {metrics?.n_feeds_today}</Typography>
      <Typography variant="h6">Largest Meal: {metrics?.largest_meal} ml</Typography>
      <Typography variant="h6">Last Meal Time: {metrics?.last_meal_time}</Typography>
      <Typography variant="h6">Pee Today: {metrics?.n_pee_today}</Typography>
      <Typography variant="h6">Poo Today: {metrics?.n_poo_today}</Typography>
      <Typography variant="h6">Suggested Meal: {metrics?.suggested_meal} ml</Typography>
    </Container>
  );
}

export default App;