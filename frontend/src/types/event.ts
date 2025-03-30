export type EventStatus = 'ongoing' | 'ended';

export interface Event {
  id: string;
  title: string;
  description: string;
  startDate: string;
  endDate: string;
  location: string;
  participants: number;
  stars: number;
  status: EventStatus;
  hasJoined: boolean;
  isCheckedIn?: boolean;
}

export interface Participant {
  id: string;
  name: string;
  avatar?: string;
  stars?: number;
} 