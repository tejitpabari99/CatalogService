create view tutor_info as
select idTutors, name, byline, linkedin, website, imageLink, group_concat(category_name) as categories from
	(select idTutors, name, byline, linkedin, resume, website, imageLink, idCategories,
		(select category from categories where catalog.idCategories=categories.idCategories) as category_name
		from tutors
		join
		catalog
		using(idTutors)) as a
group by idTutors, name, byline;