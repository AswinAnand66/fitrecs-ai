import { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Grid,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
} from '@mui/material';
import { Person as PersonIcon, Edit as EditIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import api, { Item } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { notify } from '../utils/toast';
import Navbar from '../components/Navbar';
import ContentCard from '../components/ContentCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box className="tw-py-4">{children}</Box>}
  </div>
);

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [likedItems, setLikedItems] = useState<Item[]>([]);
  const [completedItems, setCompletedItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [preferences, setPreferences] = useState({
    fitnessLevel: user?.preferences?.fitnessLevel || 'beginner',
    interests: user?.preferences?.interests || [],
    goals: user?.preferences?.goals || [],
  });

  useEffect(() => {
    const fetchUserContent = async () => {
      try {
        const [liked, completed] = await Promise.all([
          api.interactions.list({ type: 'like' }),
          api.interactions.list({ type: 'complete' }),
        ]);

        setLikedItems(liked.data);
        setCompletedItems(completed.data);
      } catch (err) {
        notify.error('Failed to load your content');
        console.error('Error fetching user content:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserContent();
  }, []);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleUpdatePreferences = async () => {
    try {
      await api.users.updatePreferences(preferences);
      await updateUser();
      setShowEditDialog(false);
      notify.success('Preferences updated successfully');
    } catch (err) {
      notify.error('Failed to update preferences');
      console.error('Error updating preferences:', err);
    }
  };

  const handleInteraction = async (type: 'view' | 'like' | 'complete', itemId: number) => {
    try {
      await api.interactions.create({
        item_id: itemId,
        interaction_type: type,
      });

      // Refresh the lists after interaction
      const [liked, completed] = await Promise.all([
        api.interactions.list({ type: 'like' }),
        api.interactions.list({ type: 'complete' }),
      ]);

      setLikedItems(liked.data);
      setCompletedItems(completed.data);
    } catch (err) {
      notify.error('Failed to update interaction');
      console.error('Error updating interaction:', err);
    }
  };

  if (isLoading || !user) {
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
          {/* Profile Header */}
          <Paper className="tw-p-8 tw-mb-8">
            <Box className="tw-flex tw-items-center tw-gap-4">
              <Avatar className="tw-w-20 tw-h-20 tw-bg-primary">
                {user.username[0].toUpperCase()}
              </Avatar>
              <Box className="tw-flex-grow">
                <Typography variant="h4" gutterBottom>
                  {user.username}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {user.email}
                </Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setShowEditDialog(true)}
              >
                Edit Preferences
              </Button>
            </Box>
          </Paper>

          {/* Content Tabs */}
          <Paper>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              className="tw-border-b"
            >
              <Tab label="Liked Content" />
              <Tab label="Completed Content" />
            </Tabs>

            <TabPanel value={activeTab} index={0}>
              {likedItems.length === 0 ? (
                <Box className="tw-text-center tw-py-8">
                  <Typography color="text.secondary">
                    You haven't liked any content yet.
                  </Typography>
                </Box>
              ) : (
                <Grid container spacing={4}>
                  {likedItems.map((item) => (
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
              )}
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              {completedItems.length === 0 ? (
                <Box className="tw-text-center tw-py-8">
                  <Typography color="text.secondary">
                    You haven't completed any content yet.
                  </Typography>
                </Box>
              ) : (
                <Grid container spacing={4}>
                  {completedItems.map((item) => (
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
              )}
            </TabPanel>
          </Paper>
        </motion.div>
      </Container>

      {/* Edit Preferences Dialog */}
      <Dialog
        open={showEditDialog}
        onClose={() => setShowEditDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Preferences</DialogTitle>
        <DialogContent>
          <Box className="tw-space-y-4 tw-py-4">
            <FormControl fullWidth>
              <InputLabel>Fitness Level</InputLabel>
              <Select
                value={preferences.fitnessLevel}
                label="Fitness Level"
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    fitnessLevel: e.target.value as string,
                  })
                }
              >
                <MenuItem value="beginner">Beginner</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Fitness Goals (comma-separated)"
              value={preferences.goals.join(', ')}
              onChange={(e) =>
                setPreferences({
                  ...preferences,
                  goals: e.target.value.split(',').map((goal) => goal.trim()),
                })
              }
              helperText="E.g., weight loss, muscle gain, flexibility"
            />

            <TextField
              fullWidth
              label="Interests (comma-separated)"
              value={preferences.interests.join(', ')}
              onChange={(e) =>
                setPreferences({
                  ...preferences,
                  interests: e.target.value
                    .split(',')
                    .map((interest) => interest.trim()),
                })
              }
              helperText="E.g., yoga, running, strength training"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEditDialog(false)}>Cancel</Button>
          <Button
            onClick={handleUpdatePreferences}
            variant="contained"
            color="primary"
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Profile;