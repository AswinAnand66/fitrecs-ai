import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  IconButton,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../auth/AuthContext';
import { notify } from '../utils/toast';
import Navbar from '../components/Navbar';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'assistant';
  timestamp: Date;
}

const FitnessCoach = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your AI fitness assistant. How can I help you today?",
      type: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input.trim(),
      type: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.ai.chat(
        userMessage.text,
        messages.slice(-5).map(m => ({
          text: m.text,
          type: m.type,
        }))
      );
      
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          type: 'assistant',
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      notify.error('Failed to get response');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tw-min-h-screen tw-bg-background">
      <Navbar />
      
      <Container maxWidth="md" className="tw-py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper className="tw-p-4 tw-min-h-[600px] tw-flex tw-flex-col">
            <Box className="tw-p-4 tw-border-b">
              <Typography variant="h5" className="tw-flex tw-items-center">
                <BotIcon className="tw-mr-2" />
                FitRecs AI Coach
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask me anything about fitness, workouts, or nutrition!
              </Typography>
            </Box>

            {/* Messages Container */}
            <Box className="tw-flex-grow tw-overflow-y-auto tw-p-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={`tw-flex tw-items-start tw-mb-4 ${
                      message.type === 'user' ? 'tw-flex-row-reverse' : ''
                    }`}
                  >
                    <Avatar
                      className={`tw-mr-2 ${
                        message.type === 'assistant'
                          ? 'tw-bg-primary'
                          : 'tw-bg-secondary'
                      }`}
                    >
                      {message.type === 'assistant' ? (
                        <BotIcon />
                      ) : (
                        <PersonIcon />
                      )}
                    </Avatar>
                    <Paper
                      className={`tw-p-3 tw-max-w-[70%] ${
                        message.type === 'user'
                          ? 'tw-bg-secondary-light tw-text-white'
                          : ''
                      }`}
                    >
                      <Typography variant="body1">{message.text}</Typography>
                      <Typography
                        variant="caption"
                        className="tw-mt-1 tw-opacity-70"
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </motion.div>
                ))}
              </AnimatePresence>
            </Box>

            {/* Input Area */}
            <Box className="tw-p-4 tw-border-t">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="tw-flex tw-gap-2"
              >
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Ask about workouts, nutrition, or fitness tips..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={isLoading}
                />
                <IconButton
                  color="primary"
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="tw-h-[56px] tw-w-[56px]"
                >
                  {isLoading ? (
                    <CircularProgress size={24} />
                  ) : (
                    <SendIcon />
                  )}
                </IconButton>
              </form>
            </Box>
          </Paper>
        </motion.div>
      </Container>
    </div>
  );
};

export default FitnessCoach;