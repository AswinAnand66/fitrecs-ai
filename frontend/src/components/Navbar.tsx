import { AppBar, Toolbar, Typography, Button, IconButton } from '@mui/material';
import {
  Fitness as FitnessIcon,
  Upload as UploadIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../auth/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static" className="bg-primary shadow-md">
      <Toolbar className="justify-between">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="flex items-center"
        >
          <IconButton
            edge="start"
            color="inherit"
            component={Link}
            to="/dashboard"
            className="mr-2"
          >
            <FitnessIcon />
          </IconButton>
          <Typography variant="h6" className="font-bold tracking-wide">
            FitRecs AI
          </Typography>
        </motion.div>

        <div className="flex items-center space-x-4">
          {user?.role === 'admin' && (
            <motion.div whileHover={{ scale: 1.05 }}>
              <Button
                color="inherit"
                component={Link}
                to="/admin/upload"
                startIcon={<UploadIcon />}
                className="font-medium"
              >
                Upload
              </Button>
            </motion.div>
          )}

          <motion.div whileHover={{ scale: 1.05 }}>
            <Button
              color="inherit"
              onClick={logout}
              startIcon={<LogoutIcon />}
              className="font-medium"
            >
              Logout
            </Button>
          </motion.div>
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;