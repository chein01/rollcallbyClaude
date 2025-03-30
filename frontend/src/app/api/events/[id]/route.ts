import { NextResponse } from 'next/server';
import { Event } from '@/types/event';

// Sample event data for demonstration
const sampleEvents: Event[] = [
  { 
    id: '1', 
    title: 'Annual Tech Conference', 
    description: 'Join us for the biggest tech event of the year with industry leaders and innovators.',
    startDate: '2023-12-15T09:00:00',
    endDate: '2023-12-15T17:00:00',
    location: 'San Francisco, CA',
    participants: 120,
    stars: 45,
    status: 'ongoing',
    hasJoined: true
  },
  { 
    id: '2', 
    title: 'Web Development Workshop', 
    description: 'Learn the latest web development techniques and tools in this hands-on workshop.',
    startDate: '2023-11-20T14:00:00',
    endDate: '2023-11-20T17:00:00',
    location: 'Online',
    participants: 85,
    stars: 32,
    status: 'ongoing',
    hasJoined: false
  },
  { 
    id: '3', 
    title: 'AI in Healthcare Symposium', 
    description: 'Explore how artificial intelligence is transforming healthcare delivery and research.',
    startDate: '2024-01-10T10:00:00',
    endDate: '2024-01-10T16:00:00',
    location: 'Boston, MA',
    participants: 95,
    stars: 38,
    status: 'ongoing',
    hasJoined: true
  },
  { 
    id: '4', 
    title: 'Mobile App Design Masterclass', 
    description: 'Master the art of creating beautiful and functional mobile app interfaces.',
    startDate: '2023-12-05T10:00:00',
    endDate: '2023-12-05T16:00:00',
    location: 'New York, NY',
    participants: 60,
    stars: 28,
    status: 'ongoing',
    hasJoined: false
  },
  { 
    id: '5', 
    title: 'Cybersecurity Summit', 
    description: 'Stay ahead of threats with insights from top cybersecurity experts.',
    startDate: '2024-02-20T09:00:00',
    endDate: '2024-02-20T17:00:00',
    location: 'Washington, DC',
    participants: 110,
    stars: 42,
    status: 'ongoing',
    hasJoined: false
  }
];

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const event = sampleEvents.find(e => e.id === params.id);

  if (!event) {
    return new NextResponse(null, { status: 404 });
  }

  return NextResponse.json(event);
}

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const event = sampleEvents.find(e => e.id === params.id);

  if (!event) {
    return new NextResponse(null, { status: 404 });
  }

  const { action } = await request.json();

  if (action === 'join') {
    event.hasJoined = true;
  } else if (action === 'star') {
    event.stars += 1;
  }

  return NextResponse.json(event);
} 