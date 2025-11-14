import { Link } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
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
import { Item } from '../api/client';

interface ContentCardProps {
  item: Item;
  onInteraction?: (type: 'view' | 'like' | 'complete') => void;
  showActions?: boolean;
  variant?: 'default' | 'compact';
}

const ContentCard: React.FC<ContentCardProps> = ({
  item,
  onInteraction,
  showActions = true,
  variant = 'default',
}) => {
  const getTypeIcon = () => {
    switch (item.type) {
      case 'workout':
        return <WorkoutIcon className="tw-text-primary" />;
      case 'article':
        return <ArticleIcon className="tw-text-secondary" />;
      case 'video':
        return <VideoIcon className="tw-text-secondary" />;
      default:
        return null;
    }
  };

  const cardContent = (
    <>
      <CardMedia
        component="img"
        height={variant === 'compact' ? 140 : 200}
        image={item.media_url || '/placeholder-fitness.jpg'}
        alt={item.title}
        className="tw-object-cover"
      />
      <CardContent>
        <Box className="tw-flex tw-items-start tw-justify-between tw-mb-2">
          <Typography
            gutterBottom
            variant={variant === 'compact' ? 'subtitle1' : 'h6'}
            component="h2"
            className="tw-line-clamp-2"
          >
            {item.title}
          </Typography>
          {getTypeIcon()}
        </Box>

        {variant === 'default' && (
          <Typography
            variant="body2"
            color="text.secondary"
            className="tw-mb-2 tw-line-clamp-2"
          >
            {item.description}
          </Typography>
        )}

        <Box className="tw-flex tw-flex-wrap tw-gap-1 tw-mb-2">
          {item.tags.slice(0, variant === 'compact' ? 2 : 3).map((tag) => (
            <Chip
              key={tag}
              label={tag}
              size={variant === 'compact' ? 'small' : 'medium'}
              className="tw-bg-primary-light tw-text-xs"
            />
          ))}
        </Box>

        <Box className="tw-flex tw-items-center tw-justify-between">
          <Box className="tw-flex tw-items-center tw-gap-2">
            <Box className="tw-flex tw-items-center">
              <TimerIcon fontSize="small" className="tw-text-gray-500" />
              <Typography variant="body2" className="tw-ml-1">
                {item.duration}m
              </Typography>
            </Box>
            <Typography
              variant="body2"
              className="tw-px-2 tw-py-1 tw-rounded tw-bg-gray-100"
            >
              {item.difficulty}
            </Typography>
          </Box>

          {showActions && (
            <Box className="tw-flex tw-gap-1">
              <Tooltip title="Like">
                <IconButton
                  size="small"
                  onClick={() => onInteraction?.('like')}
                  className="tw-text-gray-500 hover:tw-text-primary"
                >
                  <LikeIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Mark as Complete">
                <IconButton
                  size="small"
                  onClick={() => onInteraction?.('complete')}
                  className="tw-text-gray-500 hover:tw-text-secondary"
                >
                  <CompleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>
      </CardContent>
    </>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -5 }}
      className="tw-h-full"
    >
      {variant === 'compact' ? (
        <Card className="tw-h-full tw-cursor-pointer hover:tw-shadow-lg tw-transition-shadow">
          <Link
            to={`/items/${item.id}`}
            className="tw-no-underline tw-text-inherit"
            onClick={() => onInteraction?.('view')}
          >
            {cardContent}
          </Link>
        </Card>
      ) : (
        <Card className="tw-h-full hover:tw-shadow-lg tw-transition-shadow">
          {cardContent}
        </Card>
      )}
    </motion.div>
  );
};

export default ContentCard;