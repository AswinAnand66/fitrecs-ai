import { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  CircularProgress,
  Button,
} from '@mui/material';
import { motion } from 'framer-motion';
import api, { Item } from '../api/client';
import { notify } from '../utils/toast';
import Navbar from '../components/Navbar';
import RecommendationCarousel from '../components/RecommendationCarousel';
import ContentCard from '../components/ContentCard';
import { useAuth } from '../auth/AuthContext';

const Home = () => {
  const { user } = useAuth();
  const [trendingItems, setTrendingItems] = useState<Item[]>([]);
  const [personalizedItems, setPersonalizedItems] = useState<Item[]>([]);
  const [latestWorkouts, setLatestWorkouts] = useState<Item[]>([]);
  const [latestArticles, setLatestArticles] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const [trending, workouts, articles] = await Promise.all([
          api.recommendations.trending(10),
          api.items.list({ type: 'workout', limit: 6 }),
          api.items.list({ type: 'article', limit: 6 }),
        ]);

        setTrendingItems(trending.data);
        setLatestWorkouts(workouts.data);
        setLatestArticles(articles.data);

        if (user) {
          const personalized = await api.recommendations.personalized(10);
          setPersonalizedItems(personalized.data);
        }
      } catch (err) {
        notify.error('Failed to load content');
        console.error('Error fetching content:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchContent();
  }, [user]);

  const handleInteraction = async (type: 'view' | 'like' | 'complete', itemId: number) => {
    if (!user) return;

    try {
      await api.interactions.create({
        item_id: itemId,
        interaction_type: type,
      });

      if (type === 'like') {
        notify.success('Added to your favorites!');
      } else if (type === 'complete') {
        notify.success('Marked as completed!');
      }
    } catch (err) {
      notify.error('Failed to record interaction');
      console.error('Error recording interaction:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="tw-min-h-screen tw-bg-background">
        <Navbar />
        <Box className="tw-flex tw-justify-center tw-items-center tw-h-64">
          <CircularProgress />
        </Box>
      </div>
    );
  }

  return (
    <div className="tw-min-h-screen tw-bg-background">
      <Navbar />
      
      <Container maxWidth="lg" className="tw-py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Hero Section */}
          <Box className="tw-text-center tw-mb-12">
            <Typography variant="h3" component="h1" gutterBottom>
              Your Personal Fitness Journey Starts Here
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" className="tw-mb-6">
              Discover personalized workouts, health articles, and expert advice
            </Typography>
            {!user && (
              <Button
                variant="contained"
                color="primary"
                size="large"
                href="/register"
                className="tw-px-8"
              >
                Get Started
              </Button>
            )}
          </Box>

          {/* Personalized Recommendations */}
          {user && personalizedItems.length > 0 && (
            <Box className="tw-mb-8">
              <RecommendationCarousel
                title="Recommended for You"
                items={personalizedItems}
                onInteraction={handleInteraction}
              />
            </Box>
          )}

          {/* Trending Section */}
          {trendingItems.length > 0 && (
            <Box className="tw-mb-8">
              <RecommendationCarousel
                title="Trending Now"
                items={trendingItems}
                onInteraction={handleInteraction}
              />
            </Box>
          )}

          {/* Latest Workouts */}
          <Box className="tw-mb-8">
            <Typography variant="h5" className="tw-mb-4">
              Latest Workouts
            </Typography>
            <Grid container spacing={4}>
              {latestWorkouts.map((item) => (
                <Grid item xs={12} sm={6} md={4} key={item.id}>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ContentCard
                      item={item}
                      onInteraction={(type) => handleInteraction(type, item.id)}
                    />
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Latest Articles */}
          <Box>
            <Typography variant="h5" className="tw-mb-4">
              Health & Wellness Articles
            </Typography>
            <Grid container spacing={4}>
              {latestArticles.map((item) => (
                <Grid item xs={12} sm={6} md={4} key={item.id}>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ContentCard
                      item={item}
                      onInteraction={(type) => handleInteraction(type, item.id)}
                    />
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>
        </motion.div>
      </Container>
    </div>
  );
};

export default Home;