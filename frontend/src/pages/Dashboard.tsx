import { useEffect, useState } from 'react';
import { Container, Grid, Typography, Box, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import { useAuth } from '../auth/AuthContext';
import api, { Item } from '../api/client';
import ItemCard from '../components/ItemCard';
import Navbar from '../components/Navbar';

const Dashboard = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        if (user) {
          const response = await api.recommendations.hybrid(user.id);
          setRecommendations(response.data);
        }
      } catch (err) {
        setError('Failed to load recommendations');
        console.error('Error fetching recommendations:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [user]);

  const handleInteraction = async (itemId: number, type: 'view' | 'like' | 'complete') => {
    try {
      await api.interactions.create({
        item_id: itemId,
        interaction_type: type,
      });
    } catch (err) {
      console.error('Error recording interaction:', err);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <Container maxWidth="lg" className="py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h4" component="h1" className="mb-8">
            Your Personalized Fitness Recommendations
          </Typography>

          {isLoading ? (
            <Box className="flex justify-center items-center h-64">
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box className="text-center text-error py-8">
              <Typography>{error}</Typography>
            </Box>
          ) : recommendations.length === 0 ? (
            <Box className="text-center py-8">
              <Typography>No recommendations available yet.</Typography>
            </Box>
          ) : (
            <Grid container spacing={4}>
              {recommendations.map((item) => (
                <Grid item xs={12} sm={6} md={4} key={item.id}>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ItemCard
                      item={item}
                      onInteraction={(type) => handleInteraction(item.id, type)}
                    />
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          )}
        </motion.div>
      </Container>
    </div>
  );
};

export default Dashboard;