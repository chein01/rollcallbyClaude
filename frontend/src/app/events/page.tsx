'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';
import Link from 'next/link';
import './styles.css';

// Sample event data for demonstration
const sampleEvents = [
  { 
    id: '1', 
    name: 'Annual Tech Conference', 
    description: 'Join us for the biggest tech event of the year with industry leaders and innovators.',
    date: '2023-12-15',
    location: 'San Francisco, CA',
    participants: 120,
    isJoined: true
  },
  { 
    id: '2', 
    name: 'Web Development Workshop', 
    description: 'Learn the latest web development techniques and tools in this hands-on workshop.',
    date: '2023-11-20',
    location: 'Online',
    participants: 85,
    isJoined: false
  },
  { 
    id: '3', 
    name: 'AI in Healthcare Symposium', 
    description: 'Explore how artificial intelligence is transforming healthcare delivery and research.',
    date: '2024-01-10',
    location: 'Boston, MA',
    participants: 95,
    isJoined: true
  },
  { 
    id: '4', 
    name: 'Mobile App Design Masterclass', 
    description: 'Master the art of creating beautiful and functional mobile app interfaces.',
    date: '2023-12-05',
    location: 'New York, NY',
    participants: 60,
    isJoined: false
  },
  { 
    id: '5', 
    name: 'Cybersecurity Summit', 
    description: 'Stay ahead of threats with insights from top cybersecurity experts.',
    date: '2024-02-20',
    location: 'Washington, DC',
    participants: 110,
    isJoined: false
  },
];

export default function EventsPage() {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const router = useRouter();

  // Authentication check temporarily disabled
  // useEffect(() => {
  //   if (!isAuthenticated) {
  //     router.push('/auth/login');
  //   }
  // }, [isAuthenticated, router]);

  // Format date to be more readable
  const formatDate = (dateString: string) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <main className="events-container">
      <div className="events-content">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Events</h1>
          <p className="page-subtitle">Discover and join events to connect with others</p>
        </div>

        {/* Events List */}
        <div className="events-grid">
          {sampleEvents.map((event) => (
            <div key={event.id} className="event-card">
              <div className="event-header">
                <h3 className="event-title">{event.name}</h3>
                <span className="event-date">{formatDate(event.date)}</span>
              </div>
              <p className="event-description">{event.description}</p>
              <div className="event-footer">
                <div className="event-location">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <span>{event.location}</span>
                </div>
                <div className="event-participants">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                  </svg>
                  <span>{event.participants} participants</span>
                </div>
              </div>
              <Link href={`/events/${event.id}`} className="event-action-button">
                {event.isJoined ? 'View Details' : 'Join Event'}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}