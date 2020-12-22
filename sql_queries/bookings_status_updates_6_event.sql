SET GLOBAL event_scheduler = ON;
SELECT @@event_scheduler;
CREATE EVENT bookings_status_updates
ON SCHEDULE EVERY 6 HOUR
DO
	UPDATE bookings
	SET 	requestStatus = CASE WHEN requestStatus = 0 AND NOW() > meetingDate 
								THEN -1 ELSE requestStatus END,
			receiptStatus = CASE WHEN receiptStatus = 0 AND requestStatus = 1 AND NOW() > meetingDate 
								THEN -1 ELSE receiptStatus END,
		meetingStatus = CASE WHEN meetingStatus = 0 AND receiptStatus = 1 AND NOW() > meetingDate 
								THEN -1 ELSE meetingStatus END;