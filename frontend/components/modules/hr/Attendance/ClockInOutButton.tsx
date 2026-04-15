'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { LogIn, LogOut, Clock, MapPin, AlertTriangle } from 'lucide-react';
import { useCheckIn, useCheckOut } from '@/hooks/hr/useAttendance';

type ClockStatus = 'not-started' | 'in-progress' | 'completed';

interface ClockInOutButtonProps {
  employeeId: string;
  currentAttendanceId?: string;
  isCheckedIn?: boolean;
  checkInTime?: string;
  checkOutTime?: string;
  officeLatitude?: number;
  officeLongitude?: number;
  maxDistanceMeters?: number;
}

function getDistanceMeters(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function formatElapsed(ms: number): string {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export function ClockInOutButton({
  employeeId,
  currentAttendanceId,
  isCheckedIn = false,
  checkInTime,
  checkOutTime,
  officeLatitude,
  officeLongitude,
  maxDistanceMeters = 100,
}: ClockInOutButtonProps) {
  const [elapsed, setElapsed] = useState('00:00:00');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [clockOutNotes, setClockOutNotes] = useState('');
  const [geoError, setGeoError] = useState<string | null>(null);
  const lastClickRef = useRef(0);
  const checkInMutation = useCheckIn();
  const checkOutMutation = useCheckOut();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!isCheckedIn || !checkInTime) return;

    const tick = () => {
      const diff = Date.now() - new Date(checkInTime).getTime();
      setElapsed(formatElapsed(diff));
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [isCheckedIn, checkInTime]);

  const status: ClockStatus = checkOutTime
    ? 'completed'
    : isCheckedIn
      ? 'in-progress'
      : 'not-started';

  const elapsedMs = checkInTime ? Date.now() - new Date(checkInTime).getTime() : 0;
  const workedHours = elapsedMs / 3600000;
  const isOvertime = workedHours > 8;

  const validateGeoLocation = useCallback((): Promise<boolean> => {
    if (!officeLatitude || !officeLongitude) return Promise.resolve(true);

    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        setGeoError('Geolocation not supported by your browser');
        resolve(false);
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const distance = getDistanceMeters(
            position.coords.latitude,
            position.coords.longitude,
            officeLatitude,
            officeLongitude
          );
          if (distance > maxDistanceMeters) {
            setGeoError(
              `You are ${Math.round(distance)}m from the office. Maximum allowed: ${maxDistanceMeters}m`
            );
            resolve(false);
          } else {
            setGeoError(null);
            resolve(true);
          }
        },
        () => {
          setGeoError('Unable to determine your location. Please enable location services.');
          resolve(false);
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  }, [officeLatitude, officeLongitude, maxDistanceMeters]);

  const handleClockIn = async () => {
    const now = Date.now();
    if (now - lastClickRef.current < 2000) return;
    lastClickRef.current = now;

    const locationValid = await validateGeoLocation();
    if (!locationValid) return;

    checkInMutation.mutate({ employeeId });
  };

  const handleClockOutClick = () => {
    setShowConfirmDialog(true);
  };

  const handleClockOutConfirm = async () => {
    const now = Date.now();
    if (now - lastClickRef.current < 2000) return;
    lastClickRef.current = now;

    if (currentAttendanceId) {
      checkOutMutation.mutate(
        { attendanceId: currentAttendanceId },
        {
          onSuccess: () => {
            setShowConfirmDialog(false);
            setClockOutNotes('');
          },
        }
      );
    }
  };

  const isPending = checkInMutation.isPending || checkOutMutation.isPending;

  const statusBadge = (
    <Badge
      variant={
        status === 'completed' ? 'default' : status === 'in-progress' ? 'secondary' : 'outline'
      }
    >
      {status === 'completed'
        ? 'Completed'
        : status === 'in-progress'
          ? 'In Progress'
          : 'Not Started'}
    </Badge>
  );

  return (
    <>
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>{currentTime.toLocaleTimeString('en-LK')}</span>
          {statusBadge}
        </div>

        {geoError && (
          <div className="flex items-center gap-2 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
            <MapPin className="h-4 w-4 shrink-0" />
            {geoError}
          </div>
        )}

        {isCheckedIn ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2 dark:bg-green-950">
              <Clock className="h-4 w-4 text-green-600" />
              <span className="font-mono text-sm font-medium text-green-700 dark:text-green-300">
                {elapsed}
              </span>
              {isOvertime && (
                <Badge variant="outline" className="ml-1 text-amber-600 border-amber-600">
                  OT +{(workedHours - 8).toFixed(1)}h
                </Badge>
              )}
            </div>
            <Button variant="destructive" onClick={handleClockOutClick} disabled={isPending}>
              <LogOut className="mr-2 h-4 w-4" />
              {isPending ? 'Processing...' : 'Clock Out'}
            </Button>
          </div>
        ) : status === 'completed' ? (
          <div className="text-sm text-muted-foreground">Shift completed for today.</div>
        ) : (
          <Button onClick={handleClockIn} disabled={isPending}>
            <LogIn className="mr-2 h-4 w-4" />
            {isPending ? 'Processing...' : 'Clock In'}
          </Button>
        )}
      </div>

      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Clock Out</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-md bg-muted p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Check-in Time</span>
                <span className="font-medium">
                  {checkInTime ? new Date(checkInTime).toLocaleTimeString('en-LK') : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Hours Worked</span>
                <span className="font-medium">{elapsed}</span>
              </div>
              {isOvertime && (
                <div className="flex items-center justify-between text-amber-600">
                  <span className="flex items-center gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    Overtime
                  </span>
                  <span className="font-medium">+{(workedHours - 8).toFixed(1)} hours</span>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="clockout-notes">Notes (optional)</Label>
              <Textarea
                id="clockout-notes"
                value={clockOutNotes}
                onChange={(e) => setClockOutNotes(e.target.value)}
                placeholder="Add any notes about your shift..."
                maxLength={500}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleClockOutConfirm} disabled={isPending}>
              {isPending ? 'Processing...' : 'Confirm Clock Out'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
