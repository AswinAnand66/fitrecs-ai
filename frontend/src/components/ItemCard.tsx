import { Card, CardContent, CardMedia, Typography, Chip, IconButton } from '@mui/material';
import {
  Timer as TimerIcon,
  FitnessCenter as WorkoutIcon,
  Article as ArticleIcon,
  PlayCircle as VideoIcon,
  Favorite as LikeIcon,
  CheckCircle as CompleteIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Item } from '../api/client';

interface ItemCardProps {
  item: Item;
  onInteraction?: (type: 'view' | 'like' | 'complete') => Promise<void>;
}

const ItemCard: React.FC<ItemCardProps> = ({ item, onInteraction }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  const getTypeIcon = () => {
    switch (item.type) {
      case 'workout':
        return <WorkoutIcon />;
      case 'article':
        return <ArticleIcon />;
      case 'video':
        return <VideoIcon />;
      default:
        return null;
    }
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (onInteraction) {
      await onInteraction('like');
      setIsLiked(true);
    }
  };

  const handleComplete = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (onInteraction) {
      await onInteraction('complete');
      setIsCompleted(true);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="h-full"
    >
      <Link to={`/items/${item.id}`} className="h-full block">
        <Card className="h-full shadow-card hover:shadow-elevated transition-shadow duration-300">
          {item.media_url && (
            <CardMedia
              component="img"
              height="140"
              image={item.media_url}
              alt={item.title}
              className="h-36 object-cover"
            />
          )}
          <CardContent className="flex flex-col h-full">
            <div className="flex justify-between items-start mb-2">
              <Typography variant="h6" component="h3" className="font-bold text-gray-800">
                {item.title}
              </Typography>
              {getTypeIcon()}
            </div>

            <Typography
              variant="body2"
              color="textSecondary"
              className="mb-3 line-clamp-2"
            >
              {item.description}
            </Typography>

            <div className="flex flex-wrap gap-2 mb-3">
              {item.tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  size="small"
                  className="bg-secondary-light text-white"
                />
              ))}
            </div>

            <div className="mt-auto flex justify-between items-center">
              <div className="flex items-center text-gray-600">
                <TimerIcon fontSize="small" className="mr-1" />
                <Typography variant="body2">
                  {item.duration} min
                </Typography>
              </div>

              <div className="flex gap-2">
                <IconButton
                  size="small"
                  onClick={handleLike}
                  color={isLiked ? 'primary' : 'default'}
                >
                  <LikeIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={handleComplete}
                  color={isCompleted ? 'primary' : 'default'}
                >
                  <CompleteIcon />
                </IconButton>
              </div>
            </div>

            {item.similarity_score && (
              <Typography
                variant="caption"
                className="mt-2 text-gray-500"
              >
                Similarity: {Math.round(item.similarity_score * 100)}%
              </Typography>
            )}
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
};

export default ItemCard;