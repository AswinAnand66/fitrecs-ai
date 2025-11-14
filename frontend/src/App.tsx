import { ThemeProvider } from '@mui/material/styles';
import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ToastProvider } from './utils/toast';
import router from './router';
import theme from './theme';

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <ToastProvider />
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;