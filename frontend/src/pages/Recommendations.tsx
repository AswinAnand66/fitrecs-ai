import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Collapse,
  IconButton,
  Tooltip,
  Grid,
} from '@mui/material';
import {
  Help as HelpIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import api, { Item } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { notify } from '../utils/toast';
import Navbar from '../components/Navbar';
import ContentCard from '../components/ContentCard';
import RecommendationCarousel from '../components/RecommendationCarousel';

interface AIRecommendation {
  items: Item[];
  explanation: string;
}

interface ItemExplanation {
  [key: number]: string;
}

const Recommendations = () => {
  const { user } = useAuth();
  const [regularRecommendations, setRegularRecommendations] = useState<Item[]>([]);
  const [aiRecommendations, setAIRecommendations] = useState<AIRecommendation | null>(null);
  const [explanations, setExplanations] = useState<ItemExplanation>({});
  const [expandedItems, setExpandedItems] = useState<{ [key: number]: boolean }>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const [regular, contextual] = await Promise.all([
          api.recommendations.personalized(10),
          api.ai.contextualRecommendations(),
        ]);

        setRegularRecommendations(regular.data);
        setAIRecommendations(contextual.data);
      } catch (err) {
        notify.error('Failed to load recommendations');
        console.error('Error fetching recommendations:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const toggleExplanation = async (itemId: number) => {
    if (!expandedItems[itemId]) {
      // Only fetch if we haven't already
      if (!explanations[itemId]) {
        try {
          const response = await api.ai.explainRecommendation(itemId);
          setExplanations((prev) => ({
            ...prev,
            [itemId]: response.data.explanation,
          }));
        } catch (err) {
          notify.error('Failed to load explanation');
          console.error('Error fetching explanation:', err);
        }
      }
    }

    setExpandedItems((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  const handleInteraction = async (type: 'view' | 'like' | 'complete', itemId: number) => {
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
      notify.error('Failed to update interaction');
      console.error('Error updating interaction:', err);
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
          {/* AI Recommendations */}
          {aiRecommendations && aiRecommendations.items.length > 0 && (
            <Box className="tw-mb-12">
              <Paper className="tw-p-6">
                <Typography variant="h4" className="tw-mb-4">
                  Personalized for You
                </Typography>
                
                <Typography
                  variant="body1"
                  color="text.secondary"
                  className="tw-mb-6"
                >
                  {aiRecommendations.explanation}
                </Typography>

                <Grid container spacing={4}>
                  {aiRecommendations.items.map((item) => (
                    <Grid item xs={12} sm={6} md={4} key={item.id}>
                      <motion.div
                        layout
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Paper className="tw-h-full">
                          <ContentCard
                            item={item}
                            onInteraction={(type) => handleInteraction(type, item.id)}
                          />
                          
                          {/* "Why this?" section */}
                          <Box className="tw-px-4 tw-pb-2">
                            <Box className="tw-flex tw-items-center tw-justify-between">
                              <Box className="tw-flex tw-items-center tw-gap-1">
                                <HelpIcon fontSize="small" className="tw-text-gray-400" />
                                <Typography
                                  variant="body2"
                                  className="tw-text-gray-500"
                                >
                                  Why this?
                                </Typography>
                              </Box>
                              <IconButton
                                size="small"
                                onClick={() => toggleExplanation(item.id)}
                                className={`tw-transform tw-transition-transform ${
                                  expandedItems[item.id] ? 'tw-rotate-180' : ''
                                }`}
                              >
                                <ExpandMoreIcon />
                              </IconButton>
                            </Box>
                            
                            <Collapse in={expandedItems[item.id]}>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                className="tw-py-2"
                              >
                                {explanations[item.id] || 'Loading explanation...'}
                              </Typography>
                            </Collapse>
                          </Box>
                        </Paper>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Box>
          )}

          {/* Regular Recommendations */}
          {regularRecommendations.length > 0 && (
            <Box>
              <Typography variant="h5" className="tw-mb-4">
                More Workouts & Articles
              </Typography>
              <RecommendationCarousel
                items={regularRecommendations}
                onInteraction={handleInteraction}
                title="Discover More"
              />
            </Box>
          )}
        </motion.div>
      </Container>
    </div>
  );
};

export default Recommendations;