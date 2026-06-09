'use client';

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { DailyScheduleItem } from '../../types/api';

// Dynamically import FullCalendar client-side only to prevent Next.js 15 SSR window errors
const FullCalendar = dynamic(() => import('@fullcalendar/react'), { 
  ssr: false,
  loading: () => (
    <div className="h-[450px] w-full bg-slate-950/40 rounded-xl border border-slate-800 flex items-center justify-center text-xs text-slate-400">
      Loading calendar engine...
    </div>
  )
});

// Import plugins dynamically or directly (direct works client-side)
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

interface CalendarWrapperProps {
  dailySchedule: DailyScheduleItem[];
}

export function CalendarWrapper({ dailySchedule }: CalendarWrapperProps) {
  const events = useMemo(() => {
    if (!dailySchedule || dailySchedule.length === 0) return [];

    const list: any[] = [];
    const baseDate = new Date();
    // Move baseDate to nearest Monday
    const currentDay = baseDate.getDay();
    const distanceToMonday = currentDay === 0 ? -6 : 1 - currentDay;
    baseDate.setDate(baseDate.getDate() + distanceToMonday);

    dailySchedule.forEach((day) => {
      // Calculate target date for the schedule block
      const targetDate = new Date(baseDate);
      const daysToAdd = (day.week_number - 1) * 7 + (day.day_number - 1);
      targetDate.setDate(targetDate.getDate() + daysToAdd);
      const dateString = targetDate.toISOString().split('T')[0];

      day.time_blocks.forEach((block) => {
        try {
          // Parse slot e.g., "09:00 - 11:00"
          const parts = block.time_slot.split('-');
          const startStr = parts[0].trim();
          const endStr = parts[1].trim();

          list.push({
            id: `${day.week_number}-${day.day_number}-${block.task_id}`,
            title: `[${block.task_id}] ${block.name}`,
            start: `${dateString}T${startStr}:00`,
            end: `${dateString}T${endStr}:00`,
            extendedProps: {
              type: block.type,
              duration: block.duration_hours,
            },
            backgroundColor: block.type.toLowerCase().includes('deep') ? '#4f46e5' : '#7c3aed',
            borderColor: 'transparent',
            textColor: '#f8fafc',
          });
        } catch (err) {
          console.error("Failed to parse time slot:", block.time_slot, err);
        }
      });
    });

    return list;
  }, [dailySchedule]);

  return (
    <div className="w-full bg-slate-950/30 p-6 rounded-2xl border border-slate-800/80 calendar-container">
      <style jsx global>{`
        .fc {
          --fc-border-color: #1e293b;
          --fc-page-bg-color: transparent;
          --fc-list-event-hover-bg-color: #0f172a;
          color: #f8fafc;
          font-family: inherit;
        }
        .fc-theme-standard td, .fc-theme-standard th {
          border-color: rgba(255, 255, 255, 0.04);
        }
        .fc .fc-col-header-cell-cushion {
          color: #94a3b8;
          font-size: 11px;
          text-transform: uppercase;
          font-weight: 700;
          letter-spacing: 0.05em;
          padding: 8px 0;
        }
        .fc .fc-toolbar-title {
          font-size: 16px;
          font-weight: 800;
          color: #f8fafc;
        }
        .fc .fc-button-primary {
          background-color: #1e293b;
          border-color: #334155;
          color: #f8fafc;
          font-size: 12px;
          font-weight: 600;
          border-radius: 8px;
          text-transform: capitalize;
          padding: 6px 12px;
        }
        .fc .fc-button-primary:hover {
          background-color: #334155;
          border-color: #475569;
        }
        .fc .fc-button-primary:disabled {
          background-color: #0f172a;
          opacity: 0.4;
        }
        .fc .fc-button-active {
          background-color: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }
        .fc-event {
          border-radius: 6px;
          padding: 3px 6px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .fc-event-title {
          font-weight: 700;
          font-size: 10px;
        }
        .fc-timegrid-slot {
          height: 40px !important;
        }
      `}</style>
      
      {/* Renders FullCalendar component when initialized */}
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'timeGridWeek,timeGridDay'
        }}
        events={events}
        allDaySlot={false}
        slotMinTime="07:00:00"
        slotMaxTime="22:00:00"
        height="500px"
      />
    </div>
  );
}
