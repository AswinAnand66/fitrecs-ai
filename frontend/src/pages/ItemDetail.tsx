import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Chip,
  Button,
  Grid,
  CircularProgress,
  Paper,
} from '@mui/material';
import {
  Timer as TimerIcon,
  FitnessCenter as WorkoutIcon,
  Article as ArticleIcon,
  PlayCircle as VideoIcon,
  Favorite as LikeIcon,
  CheckCircle as CompleteIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../auth/AuthContext';
import api, { Item } from '../api/client';
import ItemCard from '../components/ItemCard';
import Navbar from '../components/Navbar';

const ItemDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [item, setItem] = useState<Item | null>(null);
  const [similarItems, setSimilarItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItemDetails = async () => {
      if (!id) return;
      
      setIsLoading(true);
      try {
        const [itemResponse, similarResponse] = await Promise.all([
          api.items.get(parseInt(id)),
          api.recommendations.content(parseInt(id), 5),
        ]);

        setItem(itemResponse.data);
        setSimilarItems(similarResponse.data);
        
        // Record view interaction
        if (user) {
          await api.interactions.create({
            item_id: parseInt(id),
            interaction_type: 'view',
          });
        }
      } catch (err) {
        setError('Failed to load item details');
        console.error('Error fetching item details:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchItemDetails();
  }, [id, user]);

  const handleInteraction = async (type: 'view' | 'like' | 'complete') => {
    if (!item || !user) return;

    try {
      await api.interactions.create({
        item_id: item.id,
        interaction_type: type,
      });
    } catch (err) {
      console.error('Error recording interaction:', err);
    }
  };

  const getTypeIcon = () => {
    if (!item) return null;
    
    switch (item.type) {
      case 'workout':
        return <WorkoutIcon className="text-primary" />;
      case 'article':
        return <ArticleIcon className="text-secondary" />;
      case 'video':
        return <VideoIcon className="text-secondary" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <Box className="flex justify-center items-center h-64">
          <CircularProgress />
        </Box>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <Box className="text-center text-error py-8">
          <Typography>{error || 'Item not found'}</Typography>
        </Box>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <Container maxWidth="lg" className="py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper className="p-8 shadow-card mb-8">
            <Box className="flex items-center gap-4 mb-6">
              {getTypeIcon()}
              <Typography variant="h4" component="h1">
                {item.title}
              </Typography>
            </Box>

            <Box className="mb-6">
              <Typography variant="body1" className="text-gray-700 mb-4">
                {item.description}
              </Typography>

              <Box className="flex flex-wrap gap-2 mb-4">
                {item.tags.map((tag: string) => (
                  <Chip
                    key={tag}
                    label={tag}
                    className="bg-secondary-light text-white"
                  />
                ))}
              </Box>

              <Box className="flex items-center gap-4 mb-4">
                <Box className="flex items-center gap-1">
                  <TimerIcon className="text-gray-600" />
                  <Typography variant="body2" className="text-gray-600">
                    {item.duration} minutes
                  </Typography>
                </Box>
                <Typography variant="body2" className="text-gray-600">
                  Difficulty: {item.difficulty}
                </Typography>
              </Box>

              <Box className="flex gap-4">
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<LikeIcon />}
                  onClick={() => handleInteraction('like')}
                >
                  Like
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<CompleteIcon />}
                  onClick={() => handleInteraction('complete')}
                >
                  Mark Complete
                </Button>
              </Box>
            </Box>

            {item.media_url && (
              <Box className="mb-6">
                {item.type === 'video' ? (
                  <div className="aspect-w-16 aspect-h-9">
                    <iframe
                      src={item.media_url}
                      className="w-full h-full"
                      allowFullScreen
                    />
                  </div>
                ) : (
                  <img
                    src={item.media_url}
                    alt={item.title}
                    className="w-full rounded-lg"
                  />
                )}
              </Box>
            )}
          </Paper>

          {similarItems.length > 0 && (
            <Box>
              <Typography variant="h5" className="mb-4">
                More Like This
              </Typography>
              
              <Grid container spacing={4}>
                {similarItems.map((similarItem: Item) => (
                  <Grid item xs={12} sm={6} md={4} key={similarItem.id}>
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ItemCard
                        item={similarItem}
                        onInteraction={(type: 'view' | 'like' | 'complete') => handleInteraction(type)}
                      />
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </motion.div>
      </Container>
    </div>
  );
};

export default ItemDetail;