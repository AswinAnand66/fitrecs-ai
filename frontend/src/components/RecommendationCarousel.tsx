import { useRef, useEffect, useState } from 'react';
import { Box, IconButton, Typography, useTheme, useMediaQuery } from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { Item } from '../api/client';
import ContentCard from './ContentCard';

interface RecommendationCarouselProps {
  title: string;
  items: Item[];
  onInteraction?: (type: 'view' | 'like' | 'complete', itemId: number) => void;
}

const RecommendationCarousel: React.FC<RecommendationCarouselProps> = ({
  title,
  items,
  onInteraction,
}) => {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const containerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const updateScrollButtons = () => {
    if (!containerRef.current) return;

    const { scrollLeft, scrollWidth, clientWidth } = containerRef.current;
    setCanScrollLeft(scrollLeft > 0);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
  };

  useEffect(() => {
    updateScrollButtons();
    window.addEventListener('resize', updateScrollButtons);
    return () => window.removeEventListener('resize', updateScrollButtons);
  }, [items]);

  const scroll = (direction: 'left' | 'right') => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const scrollAmount = direction === 'left' ? -400 : 400;

    container.scrollBy({
      left: scrollAmount,
      behavior: 'smooth',
    });
  };

  const handleDragEnd = (_: never, info: PanInfo) => {
    if (!containerRef.current || !isDragging) return;

    const container = containerRef.current;
    const scrollAmount = -info.offset.x * 2;
    
    container.scrollBy({
      left: scrollAmount,
      behavior: 'smooth',
    });
    
    setIsDragging(false);
  };

  return (
    <Box className="tw-relative tw-py-4">
      <Box className="tw-flex tw-justify-between tw-items-center tw-mb-4">
        <Typography variant="h5" component="h2">
          {title}
        </Typography>
        
        <Box className="tw-flex tw-gap-2">
          <IconButton
            onClick={() => scroll('left')}
            disabled={!canScrollLeft}
            className={`tw-bg-white tw-shadow-md ${
              canScrollLeft ? 'tw-opacity-100' : 'tw-opacity-50'
            }`}
          >
            <ChevronLeftIcon />
          </IconButton>
          <IconButton
            onClick={() => scroll('right')}
            disabled={!canScrollRight}
            className={`tw-bg-white tw-shadow-md ${
              canScrollRight ? 'tw-opacity-100' : 'tw-opacity-50'
            }`}
          >
            <ChevronRightIcon />
          </IconButton>
        </Box>
      </Box>

      <motion.div
        ref={containerRef}
        className="tw-overflow-x-auto tw-overflow-y-hidden tw-whitespace-nowrap tw-scrollbar-hide"
        onScroll={updateScrollButtons}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.2}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={handleDragEnd}
      >
        <AnimatePresence>
          <Box className="tw-flex tw-gap-4 tw-py-2">
            {items.map((item) => (
              <Box
                key={item.id}
                className={`tw-inline-block ${
                  isDesktop ? 'tw-w-[300px]' : 'tw-w-[250px]'
                }`}
                sx={{ minWidth: isDesktop ? 300 : 250 }}
              >
                <ContentCard
                  item={item}
                  variant="compact"
                  onInteraction={(type) => onInteraction?.(type, item.id)}
                />
              </Box>
            ))}
          </Box>
        </AnimatePresence>
      </motion.div>
    </Box>
  );
};

export default RecommendationCarousel;