import { useState, FormEvent } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Box,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  FitnessCenter as LogoIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../auth/AuthContext';
import { notify } from '../utils/toast';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(formData.email, formData.password);
      const from = location.state?.from?.pathname || '/';
      notify.success('Welcome back!');
      navigate(from, { replace: true });
    } catch (err) {
      notify.error('Invalid email or password');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" className="tw-min-h-screen tw-flex tw-items-center tw-py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="tw-w-full"
      >
        <Paper elevation={3} className="tw-p-8">
          <Box className="tw-text-center tw-mb-6">
            <LogoIcon className="tw-text-primary tw-text-5xl tw-mb-2" />
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome to FitRecs
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Sign in to continue to your fitness journey
            </Typography>
          </Box>

          <form onSubmit={handleSubmit} className="tw-space-y-4">
            <TextField
              fullWidth
              label="Email"
              type="email"
              variant="outlined"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              required
            />

            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              required
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? (
                        <VisibilityOffIcon />
                      ) : (
                        <VisibilityIcon />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={isLoading}
              className="tw-mt-4"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          <Box className="tw-text-center tw-mt-4">
            <Typography variant="body2">
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/register"
                className="tw-text-primary hover:tw-underline"
              >
                Sign up
              </Link>
            </Typography>
          </Box>
        </Paper>
      </motion.div>
    </Container>
  );
};

export default Login;