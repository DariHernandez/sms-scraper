SELECT msg_id, count(*) as counter
FROM `smsdata` 
group by msg_id
having count(*) = 2;