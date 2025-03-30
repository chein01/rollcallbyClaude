'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { CalendarDays, Users, Star, MapPin, ArrowLeft, Share2, Calendar, Heart } from 'lucide-react';
import './styles.css';

// Sample event data for demonstration
const sampleEvents = [
  { 
    id: '1', 
    title: 'Annual Tech Conference', 
    description: 'Join us for the biggest tech event of the year with industry leaders and innovators. This conference brings together tech professionals, innovators, and thought leaders from around the globe to share insights, discuss emerging trends, and showcase cutting-edge technologies. Featuring keynote speeches, panel discussions, hands-on workshops, and networking opportunities, this event is perfect for anyone looking to stay ahead in the rapidly evolving tech landscape.',
    startDate: '2023-12-15T09:00:00',
    endDate: '2023-12-15T17:00:00',
    location: 'San Francisco, CA',
    participants: 120,
    stars: 45,
    status: 'ongoing',
    hasJoined: true,
    image: '/images/tech-conference.jpg',
    organizer: 'Tech Innovators Association',
    category: 'Technology'
  },
  { 
    id: '2', 
    title: 'Web Development Workshop', 
    description: 'Learn the latest web development techniques and tools in this hands-on workshop. Designed for both beginners and intermediate developers, this workshop covers modern web technologies including HTML5, CSS3, JavaScript frameworks, responsive design principles, and performance optimization techniques. Participants will work on real-world projects and receive personalized feedback from experienced instructors.',
    startDate: '2023-11-20T14:00:00',
    endDate: '2023-11-20T17:00:00',
    location: 'Online',
    participants: 85,
    stars: 32,
    status: 'ongoing',
    hasJoined: false,
    image: '/images/web-dev.jpg',
    organizer: 'CodeMasters Academy',
    category: 'Education'
  },
  { 
    id: '3', 
    title: 'AI in Healthcare Symposium', 
    description: 'Explore how artificial intelligence is transforming healthcare delivery and research. This symposium brings together healthcare professionals, researchers, and AI specialists to discuss the latest applications of artificial intelligence in medical diagnostics, treatment planning, drug discovery, and patient care. Learn about breakthrough technologies, ethical considerations, and future possibilities at the intersection of AI and healthcare.',
    startDate: '2024-01-10T10:00:00',
    endDate: '2024-01-10T16:00:00',
    location: 'Boston, MA',
    participants: 95,
    stars: 38,
    status: 'ongoing',
    hasJoined: true,
    image: '/images/ai-healthcare.jpg',
    organizer: 'Healthcare Innovation Institute',
    category: 'Healthcare'
  },
  { 
    id: '4', 
    title: 'Mobile App Design Masterclass', 
    description: 'Master the art of creating beautiful and functional mobile app interfaces. This comprehensive masterclass covers the entire mobile app design process, from user research and wireframing to prototyping and visual design. Learn proven design principles, UX methodologies, and how to create intuitive navigation patterns that enhance user engagement. Participants will gain hands-on experience with industry-standard design tools and leave with a polished portfolio piece.',
    startDate: '2023-12-05T10:00:00',
    endDate: '2023-12-05T16:00:00',
    location: 'New York, NY',
    participants: 60,
    stars: 28,
    status: 'ongoing',
    hasJoined: false,
    image: '/images/app-design.jpg',
    organizer: 'Design Excellence Guild',
    category: 'Design'
  },
  { 
    id: '5', 
    title: 'Cybersecurity Summit', 
    description: 'Stay ahead of threats with insights from top cybersecurity experts. This summit addresses the latest security challenges facing organizations today, including ransomware, social engineering, cloud security vulnerabilities, and IoT threats. Sessions feature case studies, live demonstrations, and strategic frameworks from industry leaders and security practitioners. Attendees will learn practical strategies for strengthening their security posture and responding effectively to evolving cyber threats.',
    startDate: '2024-02-20T09:00:00',
    endDate: '2024-02-20T17:00:00',
    location: 'Washington, DC',
    participants: 110,
    stars: 42,
    status: 'ongoing',
    hasJoined: false,
    image: '/images/cybersecurity.jpg',
    organizer: 'Global Security Alliance',
    category: 'Security'
  }
];

// Helper function to format date
const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { 
    weekday: 'long',
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [event, setEvent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate API call with sample data
    setLoading(true);
    const foundEvent = sampleEvents.find(e => e.id === params.id);
    
    setTimeout(() => {
      if (foundEvent) {
        setEvent(foundEvent);
      } else {
        setError('Event not found');
      }
      setLoading(false);
    }, 500); // Add small delay to simulate API call
  }, [params.id]);

  const handleJoinEvent = async () => {
    // Simulate API call
    setEvent((prev: any) => ({
      ...prev,
      hasJoined: true
    }));
  };

  const handleStarEvent = async () => {
    // Simulate API call
    setEvent((prev: any) => ({
      ...prev,
      stars: prev.stars + 1
    }));
  };

  if (loading) {
    return (
      <div className="event-detail-loading">
        <div className="loading-spinner" />
        <p>Loading event details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="event-detail-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="event-detail-error">
        <p>Event not found</p>
      </div>
    );
  }

  const isEventEnded = new Date(event.endDate) < new Date();

  return (
    <div className="event-detail-container">
      <div className="event-detail-back">
        <button 
          onClick={() => router.back()} 
          className="back-button"
        >
          <ArrowLeft size={20} />
          <span>Back to Events</span>
        </button>
      </div>

      <div className="event-detail-layout">
        {/* Left Column - Image */}
        <div className="event-detail-image-container">
          <div className="event-image-wrapper">
            <div className={`event-placeholder-image ${event.category.toLowerCase()}`}>
              <h3 className="placeholder-title">{event.title}</h3>
            </div>
            <div className="event-image-overlay">
              <div className="event-category-badge">{event.category}</div>
            </div>
          </div>
          
          <div className="event-actions-card">
            <div className="event-date-badge">
              <Calendar className="h-5 w-5" />
              <div>
                <p className="date-badge-day">{new Date(event.startDate).getDate()}</p>
                <p className="date-badge-month">{new Date(event.startDate).toLocaleString('default', { month: 'short' })}</p>
              </div>
            </div>
            
            <div className="event-action-buttons">
              <button 
                className="action-button star"
                onClick={handleStarEvent}
                disabled={isEventEnded}
              >
                <Star size={20} />
                <span>{event.stars}</span>
              </button>
              
              <button className="action-button share">
                <Share2 size={20} />
                <span>Share</span>
              </button>
              
              <button className="action-button favorite">
                <Heart size={20} />
                <span>Save</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Right Column - Event Details */}
        <div className="event-detail-info-container">
          <div className="event-detail-header-card">
            <h1 className="event-detail-title">{event.title}</h1>
            
            <div className="event-organizer">
              <span className="organizer-label">Organized by</span>
              <span className="organizer-name">{event.organizer}</span>
            </div>
            
            <div className="event-meta-info">
              <div className="meta-item">
                <CalendarDays className="h-5 w-5" />
                <div>
                  <p className="meta-label">When</p>
                  <p className="meta-value">{formatDate(event.startDate)}</p>
                </div>
              </div>
              
              <div className="meta-item">
                <MapPin className="h-5 w-5" />
                <div>
                  <p className="meta-label">Where</p>
                  <p className="meta-value">{event.location}</p>
                </div>
              </div>
              
              <div className="meta-item">
                <Users className="h-5 w-5" />
                <div>
                  <p className="meta-label">Participants</p>
                  <p className="meta-value">{event.participants} attending</p>
                </div>
              </div>
              
              <div className="meta-item">
                <div>
                  <p className="meta-label">Status</p>
                  <p className={`status-badge ${isEventEnded ? 'ended' : 'ongoing'}`}>
                    {isEventEnded ? 'Ended' : 'Ongoing'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="join-event-container">
              <button 
                className={`join-event-button ${event.hasJoined ? 'joined' : ''} ${isEventEnded ? 'ended' : ''}`}
                onClick={handleJoinEvent}
                disabled={isEventEnded || event.hasJoined}
              >
                {event.hasJoined ? 'Already Joined' : isEventEnded ? 'Event Ended' : 'Join Event'}
              </button>
              <p className="join-text">
                {event.hasJoined ? 
                  'You have successfully joined this event' :
                  isEventEnded ?
                  'This event has already ended' :
                  'Join this event to receive updates and connect with other participants'}
              </p>
            </div>
          </div>
          
          <div className="event-detail-description-card">
            <h2 className="section-title">About this event</h2>
            <div className="description-content">{event.description}</div>
          </div>
        </div>
      </div>
    </div>
  );
} 