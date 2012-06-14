CREATE VIEW submissions_values_view AS
SELECT
    d.id as submission, b.id AS value_id, a.name, a.slug,
    CASE WHEN a.datatype = 'int' THEN
        ''||b.value_int
    WHEN a.datatype = 'text' THEN
        ''||b.value_text
    WHEN a.datatype = 'float' THEN
        ''||b.value_float
    WHEN a.datatype = 'bool' THEN
        ''||b.value_bool
    WHEN a.datatype = 'date' THEN
        ''||b.value_date
    ELSE ''
    END AS value
FROM
    eav_attribute a, eav_value b, rapidsms_xforms_xformsubmissionvalue c, rapidsms_xforms_xformsubmission d
WHERE
    b.attribute_id = a.id AND (b.id = c.value_ptr_id AND (c.submission_id = d.id));

CREATE VIEW xform_submissions_view2 AS
SELECT
    a.id AS submissionid, b.name AS report, b.keyword, a.created AS "date",
    d.name AS reporter, d.id AS reporter_id, c.identity AS phone,
    -- get_contact_facility_code(d.id) AS facility,
    a.has_errors,
    f.code AS facility
FROM rapidsms_xforms_xformsubmission a, rapidsms_xforms_xform b, rapidsms_connection c, rapidsms_contact d,
    healthmodels_healthproviderbase e, healthmodels_healthfacilitybase f
WHERE
    a.has_errors = False
    AND a.xform_id = b.id
    AND a.connection_id IS NOT NULL
    AND b.keyword
        IN ('com', 'mal', 'rutf', 'epi', 'home', 'birth', 'muac', 'opd', 'test', 'treat', 'rdt', 'act', 'qun', 'cases', 'death')
        -- IN ('test', 'treat', 'act', 'cases', 'death')
    AND (a.connection_id = c.id AND c.contact_id = d.id)
    AND (d.id = e.contact_ptr_id AND e.facility_id = f.id)
ORDER BY
    a.created DESC;


CREATE VIEW all_submission_values_view AS
SELECT
    a.submissionid, a.report, a.keyword, a.date, a.facility, a.reporter, a.phone, a.has_errors,
    b.name, b.slug, b.value
FROM
    xform_submissions_view2 a, submissions_values_view b
WHERE
    (a.submissionid = b.submission) AND (facility  IS NOT NULL AND value <> '')
ORDER BY
    a.submissionid ASC;
