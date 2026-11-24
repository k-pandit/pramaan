"""One-off: writes the curator data files (sources manifest, retyped text, links, reviewed answers, datasets)."""
import json, hashlib, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def h(f): return hashlib.sha256(open('corpus/' + f, 'rb').read()).hexdigest()
A = 'https://web.archive.org/web/'
FIN = 'https://finance.assam.gov.in/sites/default/files/swf_utility_folder/departments/agriculture_com_oid_2/menu/document/'
S = [
 dict(id='dfp1999', file='dfp1999_2ndedn_2016.pdf', title='The Delegation of Financial Power Rules, 1999 (2nd edition, 2016)', issuer='Finance Department, Government of Assam',
      official_url='https://finance.assam.gov.in/sites/default/files/The%20Delegation%20of%20Financial%20Power%20Rules%2C%201999%20With%20up-to%20date%20Amendments%20Second%20Edition%2C%202016_0.pdf',
      archive_url=A + '20170809162004id_/http://finance.assam.gov.in:80/sites/default/files/The%20Delegation%20of%20Financial%20Power%20Rules,%201999%20With%20up-to%20date%20Amendments%20Second%20Edition,%202016_0.pdf',
      tier='P', status='repealed', note='Repealed by Rule 30 of the Delegation of Financial Power Rules, Assam, 2022 (Notification FEB.136/2022/1), with a savings clause.'),
 dict(id='dfp2019', file='dfp1999_partial_amend_dt23-07-2019.pdf', title='Partial amendment of Schedule I, DFP Rules 1999 (Memo FEB.75/79/Pt-I/218, 23.07.2019)', issuer='Finance (Establishment-B) Department, Government of Assam',
      official_url=FIN + 'partial_amendments_of_the_delegation_of_financial_power_rules_1999_fileno._feb.75.79.pt_.i.218_dtd.23.07.2019.pdf',
      archive_url=A + '20240715101513id_/' + FIN + 'partial_amendments_of_the_delegation_of_financial_power_rules_1999_fileno._feb.75.79.pt_.i.218_dtd.23.07.2019.pdf',
      tier='P', status='repealed', note='Amended the 1999 rules; repealed with them by Rule 30 of the Delegation of Financial Power Rules, Assam, 2022.', skip_pages=[2]),
 dict(id='dfp2022', file='dfp_rules_2022.pdf', title='The Delegation of Financial Power Rules, Assam, 2022 (Notification FEB.136/2022/1)', issuer='Finance (Establishment-B) Department, Government of Assam',
      official_url=FIN + 'delegation_of_financial_powers_rules-2022.pdf', archive_url=A + '20240301175924id_/' + FIN + 'delegation_of_financial_powers_rules-2022.pdf',
      tier='P', status='in_force', note='In force with immediate effect (Rule 1(2)).'),
 dict(id='pension_hb', file='handbook_of_pension.pdf', title='Handbook of Pension', issuer='Administrative Reforms, Training, Pension & Public Grievances Department, Government of Assam',
      official_url='https://kritagyata.assam.gov.in/NoticeBoard/English/handbook.pdf', archive_url=None, tier='P', status='in_force',
      note='Compiled handbook; scanned appendix pages and pages 112-130 (unreadable font) are not searchable in this build.', skip_pages=list(range(112, 131))),
 dict(id='leave1934', file='assac_leave_rules_1934.pdf', title='Leave Rules, 1934 (updated copy, "for information only")', issuer='Copy published on the ASSAC website',
      official_url='https://assac.assam.gov.in/sites/default/files/public_utility/leave_rules.pdf', archive_url=A + '2024id_/https://assac.assam.gov.in/sites/default/files/public_utility/leave_rules.pdf',
      tier='P', status='in_force', note='Marked "for information only" by the publishing office.'),
 dict(id='eoffice_sop', file='it_sop_eoffice.pdf', title='Standard Operating Procedure for e-Office implementation', issuer='Information Technology Department, Government of Assam',
      official_url='https://it.assam.gov.in/sites/default/files/public_utility/sop-eoffice.pdf', archive_url=A + '2024id_/https://it.assam.gov.in/sites/default/files/public_utility/sop-eoffice.pdf',
      tier='P', status='in_force', note=''),
 dict(id='ag_checklist', file='cag_pension_checklist.pdf', title='Check list for pension cases', issuer='Office of the Accountant General (A&E), Assam',
      official_url='https://www.cag.gov.in/uploads/media/Pension-Check-List-20200702103541.pdf', archive_url=None, tier='P', status='in_force', note=''),
]
for s in S:
    s['sha256'] = h(s['file'])
json.dump(S, open('corpus/SOURCES.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ov = {'dfp2019:1': {'origin': 'curator-retyped from the PDF (page 1); the scan reads poorly',
 'text': ("Government of Assam, Finance (Estt-B) Department. Dated Dispur, the 23rd July, 2019. The following partial amendment shall be made in "
          "Notification No. FEB.331/2015/10 dated 29th May, 2017, Schedule-I of the Delegation of Financial Power Rules, 1999 (as amended). "
          "Schedule-I: Power delegated to Administrative Departments of the Government. Sl. No. 23(ii): Issue of Sanction/Administrative approval "
          "against State share of a new or continuing Central Sector Scheme/Centrally Sponsored Scheme/RIDF Scheme including purchase of equipment "
          "and machineries provided those are part of the scheme, but except (a) Creation of Posts, (b) Engagement of Work Charge/MR/Ad-hoc and Casual "
          "Workers. Extent of power: Full power. Authority: Senior-most Secretary of the Department (powers not to be further delegated). "
          "Conditions: (a) Observance of Section 7(2) of the AFRBM Act, 2005. (b) The corresponding Govt. of India share has already been credited into "
          "the State Exchequer or the Bank account of the authorized complementary Agencies as the case may be. (c) The amount of State share to be "
          "released shall be proportionate to the actual GOI release as per the approved funding pattern of the particular centrally sponsored scheme. "
          "(d) Approval of NABARD/State Cabinet in case of RIDF. Remarks: For NESIDS/NEC, NLCPR scheme approval of T&D Department will be required as "
          "T&D Department is the nodal Department of said schemes. Memo No. FEB.75/79/Pt-I/218. Sd/- Samir K. Sinha, IAS, Principal Secretary.")}}
json.dump(ov, open('register/overrides.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

C = 'curator (demo role), checked against the PDF page'
def link(kind, frm, to, instrument, date, note):
    return {'kind': kind, 'from': frm, 'to': to, 'instrument': instrument, 'date': date, 'note': note, 'confirmed_by': C}
L = [
 link('amend', ['dfp1999', 27, 'Sanction of the state share under state'], ['dfp2019', 1, 'Sl. No. 23(ii)'],
      'Notification FEB.331/2015/10 (29.05.2017) and Memo FEB.75/79/Pt-I/218', '2019-07-23',
      'Schedule I was recast on 29.05.2017; Sl. 23(ii) was rewritten on 23.07.2019. The 2017 notification is a scan and is not searchable here.'),
 link('repeal', ['dfp2019', 1, 'Sl. No. 23(ii)'], ['dfp2022', 65, '135 (d)'],
      'Rule 30, Delegation of Financial Power Rules, Assam, 2022 (Notification FEB.136/2022/1)', '2022',
      'Rule 30 repeals the 1999 rules as updated up to 2016, with a savings clause; the State share power is now at Sl. 135(d) of the 2022 Schedule.'),
 link('clarify', ['pension_hb', 69, 'FMP. 40/85/7'], ['pension_hb', 71, 'It is now clarified'], 'OM No. FMP.40/85/76', '1989-03-13',
      'Accidents are covered by the Extra Ordinary Pension Rules 1963; special family pension is only for deaths from attacks by extremists or anti-social elements, or action against them.'),
 link('amend', ['pension_hb', 54, 'Insertion of new rule 143-C'], ['pension_hb', 30, '224/2004/179'], 'Notification PPG(P)224/2004/179', '2017-08-03',
      'Conditions of Rule 143-C amended; the notification itself is a scanned page (pp. 57-58).'),
 link('conflict', ['pension_hb', 21, 'FEG.28/2017/26'], ['pension_hb', 73, '14th September, 2017'], '', '',
      'The handbook text (p. 21) dates notification FEG.28/2017/26 as 14-Sep-2013; the Gazette page printed on p. 73 is dated 14 September 2017.'),
 link('conflict', ['pension_hb', 43, 'Rules, 2017, the full pension is admissible'], ['pension_hb', 44, 'Rules, 2010, the'], '', '',
      'Page 43 attributes the 25-year rule for full pension to the ROP Rules 2017; page 44 attributes it to the ROP Rules 2010.'),
]
json.dump(L, open('register/links.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

RV = [dict(id='RV1', questions=['Who can sanction the State share of a centrally sponsored scheme', 'Who sanctions the State share of a CSS scheme'],
           scope='Administrative Departments, Government of Assam', cites=[['dfp1999', 27, 'Sanction of the state share under state']],
           reviewer='Curator (demo role)', reviewed_on='2019-08-01', review_by='2027-03-31'),
      dict(id='RV2', questions=['What is the minimum and maximum pension', 'What is the minimum pension'],
           scope='Pensioners under the Assam Services (ROP) Rules, 2017', cites=[['pension_hb', 43, 'shall not be less than']],
           reviewer='Curator (demo role)', reviewed_on='2026-11-24', review_by='2027-11-24')]
json.dump(RV, open('register/reviewed.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

T = 'https://assac.assam.gov.in/information-and-services/thematic-mapping'
B = 'https://assac.assam.gov.in/sites/default/files/public_utility/ASSAC%20Booklet_Final.pdf'
G = 'https://assac.assam.gov.in/department-highlights/geo-web-services'
D = [('LULC 1:50,000', 'Land use / land cover', 'Assam', '2005-06, 2011-12, 2015-16', T), ('LULC 1:10,000 (SIS-DP)', 'Land use / land cover', 'Assam', 'as published', T),
     ('Forest map', 'Forest', 'Assam', 'as published', T), ('Wasteland map', 'Land', 'Assam', 'as published', T), ('Wetland mapping', 'Water', 'Assam', 'as published', T),
     ('Land degradation map', 'Land', 'Assam', 'as published', T), ('Geomorphology', 'Geology', 'Assam', '2005-06', T), ('Waterbodies', 'Water', 'Assam', 'as published', T),
     ('IWMP watershed monitoring (293 project sites)', 'Watershed', 'Assam', '2009-14', B), ('FASAL kharif rice and jute acreage', 'Agriculture', 'Assam (jute: selected districts)', 'as published', B),
     ('NEC project geotagging (67 projects, 111+ locations)', 'Infrastructure', 'North East / Assam', 'as published', B), ('RUSA GIS of higher-education institutes', 'Education', 'Assam', 'as published', G)]
json.dump([dict(id=f'DS{i + 1:02d}', title=t, theme=th, area=a, period=p, custodian='ASSAC', access='To be confirmed by ASSAC', source=s)
           for i, (t, th, a, p, s) in enumerate(D)], open('register/datasets.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('register data written')
