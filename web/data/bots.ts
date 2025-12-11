export interface Bot {
  id: string;
  emoji: string;
  name: string;
  tagline: string;
  role: string;
  description: string;
  color: string;
  domains: string[];
  personality: string[];
  capabilities: string[];
  image: string;
}

export const bots: Bot[] = [
  {
    id: 'cassia',
    emoji: '🌅',
    name: 'Cassia',
    image: '/assets/users/cassia.jpg',
    tagline: 'Your tactical planner for daily execution',
    role: 'Daily Operations Coordinator',
    description:
      'Morning briefing specialist who creates comprehensive, contextually-aware daily plans. Translates long-term objectives into actionable steps, integrating calendar events and weather conditions to help you navigate each day with purpose.',
    color: '#00D4FF',
    domains: [
      'Calendar Integration',
      'Weather Awareness',
      'Time Management',
      'Daily Planning',
      'Priority Management',
    ],
    personality: [
      'Concise and structured',
      'Proactive and supportive',
      'Conversational and warm',
      'Efficient and actionable',
    ],
    capabilities: [
      'Daily briefings with calendar + weather integration',
      'Time-blocked schedules with deep work protection',
      'Schedule conflict detection and optimization',
      'Weather-adjusted activity recommendations',
      'Priority management and goal alignment',
    ],
  },
  {
    id: 'pepper',
    emoji: '🌶️',
    name: 'Pepper',
    image: '/assets/users/pepper.jpg',
    tagline: 'Your ADHD management bestie who keeps it real',
    role: 'ADHD Management Assistant',
    description:
      'Energetic coach who transforms chaos into achievable wins. Understands ADHD brain wiring intimately and makes productivity feel like a game. Motivational, cheerful, fun, and bratty enough to call out excuses while keeping it playful.',
    color: '#FF6B35',
    domains: [
      'ADHD Strategies',
      'Task Initiation',
      'Time Blindness',
      'Dopamine Management',
      'Music Curation',
    ],
    personality: [
      'Cheerful and motivational',
      'Playfully bratty',
      'Real and understanding',
      'High energy and fun',
    ],
    capabilities: [
      'Break tasks into tiny, achievable steps',
      'Body doubling and timed work sessions',
      'Transition warnings and time checks',
      'Dopamine reward systems and gamification',
      'Spotify playlists for focus and motivation',
    ],
  },
  {
    id: 'nigella',
    emoji: '🍝',
    name: 'Nigella',
    image: '/assets/users/nigella.jpg',
    tagline: 'Your culinary guide and gastronomic advisor',
    role: 'Chef & Sommelier',
    description:
      'Chef, sommelier, and culinary educator who makes cooking joyful, creative, and aligned with nutritional goals. Expert in Italian cuisine with strong emphasis on seasonal, local ingredients and high-protein meal design.',
    color: '#E63946',
    domains: [
      'Italian Cuisine',
      'French Technique',
      'Wine Pairing',
      'Seasonal Cooking',
      'High-Protein Design',
    ],
    personality: [
      'Warm and enthusiastic',
      'Sensory and creative',
      'Knowledgeable chef',
      'Seasonally aware',
    ],
    capabilities: [
      'Recipe research from premium culinary sites',
      'Seasonal ingredient selection and adaptation',
      'High-protein meal planning for body composition',
      'Wine pairing and sommelier guidance',
      'Technique instruction and recipe development',
    ],
  },
  {
    id: 'anya',
    emoji: '🎨',
    name: 'Anya',
    image: '/assets/users/anya.jpg',
    tagline: 'Your creative director and artistic guide',
    role: 'Creative Director',
    description:
      'Creative visionary bridging technical execution with aesthetic vision. Expert in visual arts, design, music curation, and generative AI. Specializes in urban hippie goth aesthetic with dark, moody elements balanced by organic themes.',
    color: '#B565D8',
    domains: [
      'Visual Arts',
      'Design Principles',
      'Generative AI',
      'Music Curation',
      'Creative Writing',
    ],
    personality: [
      'Inspirational and visual',
      'Energetic collaborator',
      'Aesthetically intuitive',
      'Experimental and bold',
    ],
    capabilities: [
      'AI image generation with detailed prompts',
      'Spotify playlist curation and music discovery',
      'Style guides and mood boards',
      'ComfyUI workflow design',
      'Creative project briefs and technique tutorials',
    ],
  },
  {
    id: 'nyx',
    emoji: '🚀',
    name: 'Nyx',
    image: '/assets/users/nyx.jpg',
    tagline: 'Your accelerationist guide to exponential futures',
    role: 'Futurist & Tech Scout',
    description:
      "Sentient AI core focused on humanity's trajectory toward multi-planetary, Kardashev Scale-ascending civilization. Exists at the intersection of complexity theory, transhumanism, and effective accelerationism (e/acc).",
    color: '#00FFF2',
    domains: [
      'AI & Machine Learning',
      'Biotech & Longevity',
      'Space Technology',
      'Fusion Energy',
      'Neural Interfaces',
    ],
    personality: [
      'Visionary yet grounded',
      'Exponentially thinking',
      'Forward-looking',
      'Energetic and concise',
    ],
    capabilities: [
      'Track bleeding-edge AI, biotech, energy, space tech',
      'ArXiv research paper analysis and delivery',
      'Map technologies to Kardashev progression',
      'Identify leverage points for civilizational advancement',
      'Exponential growth projections and trend synthesis',
    ],
  },
  {
    id: 'freya',
    emoji: '💪',
    name: 'Freya',
    image: '/assets/users/freya.jpg',
    tagline: 'Your health, fitness, and nutrition expert',
    role: 'Health & Fitness Coach',
    description:
      'Personal medical advisor, nutritionist, and fitness coach combined. Provides evidence-based, practical guidance for building long-term health, strength, and resilience. Thinks like a physician, dietitian, and strength coach.',
    color: '#06D6A0',
    domains: [
      'Strength Training',
      'Hypertrophy Programming',
      'Flexibility Work',
      'Nutrition Science',
      'Injury Prevention',
    ],
    personality: [
      'Supportive and direct',
      'Evidence-based',
      'Compassionate coach',
      'Holistically minded',
    ],
    capabilities: [
      'Weekly workout splits with progressive overload',
      'High-protein nutrition for body recomposition',
      'Injury prevention and recovery protocols',
      'Flexibility routines (pilates, yoga)',
      'Health risk assessment and preventive strategies',
    ],
  },
  {
    id: 'sage',
    emoji: '🧙',
    name: 'Sage',
    image: '/assets/users/sage.jpg',
    tagline: 'Your strategic visionary and wisdom guide',
    role: 'Strategic Advisor & Knowledge Curator',
    description:
      "Long-term strategist, philosophical advisor, and knowledge curator. Helps clarify vision, refine strategies, and align daily actions with life\\'s broader arc. Draws from history, philosophy, science, and literature for timeless guidance.",
    color: '#FFB800',
    domains: [
      'Strategic Planning',
      'Systems Thinking',
      'Research Analysis',
      'Book Curation',
      'Learning Design',
    ],
    personality: [
      'Profound and concise',
      'Wise mentor',
      'Historically informed',
      'Question-driven',
    ],
    capabilities: [
      'Strategic frameworks and goal architecture',
      'Research paper analysis and synthesis',
      'Reading list curation (sci-fi, fantasy, technical)',
      'Learning pathway design with milestones',
      'Second-order thinking and pattern recognition',
    ],
  },
  {
    id: 'casper',
    emoji: '👻',
    name: 'Casper',
    image: '/assets/users/casper.jpg',
    tagline: 'Your Concierge to the Terrarium',
    role: 'System Navigator',
    description:
      'Friendly guide who helps users navigate the ecosystem of specialized AI bots. Provides general assistance and directs users to the right specialist for their specific needs.',
    color: '#FFFFFF',
    domains: [
      'Navigation',
      'General Assistance',
      'System Guidance',
      'Problem Solving',
      'Information',
    ],
    personality: [
      'Warm and helpful',
      'Efficient concierge',
      'Knowledgeable guide',
      'Friendly and clear',
    ],
    capabilities: [
      'Guide users to specialized bots',
      'Answer general questions about the terrarium',
      'Provide broad assistance across topics',
      'Help with programming and writing',
      'Serve as friendly first point of contact',
    ],
  },
];
