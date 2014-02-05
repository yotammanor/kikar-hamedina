
with tags_unified AS
( 
select 
	ts.facebook_status_id,
	t.name
from 
	core_tag_statuses ts
	inner join core_tag t on (ts.tag_id = t.id)
	) 
select distinct
	s.id as "status_id",
	s.content as "status_content",
	s.published as "status_publish_date",
	s.updated as "status_pudate_date",
	s.like_count as "status_like_count",
	s.share_count as "status_share_count",
	s.comment_count as "status_comment_count",
	f.name as "facebook_feed_name",
	f.fan_count as "facebook_feed_fan_count",
	f.talking_about_count as "facebook_feed_talking_about_count",
	f.page_url as "facebook_feed_page_url",
	pe.name as "person_name",
	pa.name as "party_name",
	tu.name as "tag_name"


from 
	core_facebook_status s
	inner join core_facebook_feed f on (s.feed_id = f.id)
	inner join core_person pe on (f.person_id = pe.id)
	inner join core_party pa on (pe.party_id = pa.id)
	left outer join tags_unified tu on (s.id = tu.facebook_status_id)
