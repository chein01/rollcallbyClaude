import { apiService } from '@/services/api';
import { Event } from '@/types/event';
import { ApiResponse } from '@/types/api';

export const eventsEndpoints = {
  getEvents: () => {
    return apiService.get<Event[]>('/events');
  },
  getEvent: (id: string) => {
    return apiService.get<Event>(`/events/${id}`);
  },
  joinEvent: (id: string) => {
    return apiService.post<void>(`/events/${id}/join`);
  },
  checkIn: (id: string) => {
    return apiService.post<void>(`/events/${id}/checkin`);
  },
  starEvent: (id: string) => {
    return apiService.post<void>(`/events/${id}/star`);
  }
}; 