from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
import json
from datetime import datetime
import os
import sys

# Configuration paths
SIMILARITY_JSON_PATH = "/Users/hardikchoudhary/Documents/Fid/Resume_Analyzer/Dif_Resume_Analyzer/Bins_result/Bin_similarity_score.json"  # Path for bin_similarity_score.json
CANDIDATE_JSON_PATH = "/Users/hardikchoudhary/Documents/Fid/Resume_Analyzer/Dif_Resume_Analyzer/Bins_result/candidate_data.json"         # Path for candidate_data.json
OUTPUT_FOLDER_PATH = "/Users/hardikchoudhary/Documents/Fid/Resume_Analyzer/Dif_Resume_Analyzer/Report/V3_Report/reports"                           # Folder to store generated reports

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file - {file_path}")
        sys.exit(1)
        

def create_label_box(score):
    """Create label based on score"""
    if score >= 60:
        return ('GOOD', colors.green, '✓')  # Check mark for good
    elif 30 <= score < 60:
        return ('NEUTRAL', colors.orange, '○')  # Circle for neutral
    else:
        return ('POOR', colors.red, '■')  # Square for poor

def format_score(score):
    """Convert score to percentage"""
    try:
        return float(score) * 100
    except (ValueError, TypeError):
        return 0.0

def split_skill_gap_analysis(text):
    """Split skill gap analysis into bullet points"""
    sections = {
        "Non-Negotiable Skills Missing": "",
        "Negotiable Skills Missing": "",
        "Optional Skills Missing": "",
        "Key Upskilling Recommendations": ""
    }
    
    current_section = None
    for part in text.split('. '):
        for section in sections.keys():
            if section in part:
                current_section = section
                sections[current_section] = part
                break
            elif current_section and part:
                sections[current_section] += ". " + part
    
    return sections
def generate_score_summary(elements, scores_summary, header_style):
    """
    Generate a modified score summary section with colored symbols
    that fits within page width
    """
    elements.append(Paragraph("Score Summary", header_style))
    
    # Split scores into two rows for better fit
    first_row = scores_summary[:5]  # First 5 scores
    second_row = scores_summary[5:]  # Remaining scores
    
    def create_summary_row(scores_list):
        headers = [[name for name, _ in scores_list]]
        symbols = []
        
        for _, score in scores_list:
            _, color, symbol = create_label_box(score)
            # Create a colored symbol cell with proper styling
            if symbol == '✓':
                #colored_symbol = f'<font color="green">{symbol}</font>'
                colored_symbol = symbol
            elif symbol == '○':
                #colored_symbol = f'<font color="yellow">{symbol}</font>'
                colored_symbol = symbol
            else:  # square
                #colored_symbol = f'<font color="red">{symbol}</font>'
                colored_symbol = symbol
            symbols.append(colored_symbol)
            
        headers.append(symbols)
        return headers
    
    # Create two tables for the split data
    first_table = Table(
        create_summary_row(first_row),
        colWidths=[1.2*inch] * len(first_row)
    )
    
    second_table = Table(
        create_summary_row(second_row),
        colWidths=[1.2*inch] * len(second_row)
    )
    
    # Common style for both tables
    table_style = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 1), (-1, 1), 16),  # Slightly larger symbols
    ]
    
    first_table.setStyle(TableStyle(table_style))
    second_table.setStyle(TableStyle(table_style))
    
    elements.append(first_table)
    elements.append(Spacer(1, 10))  # Add space between tables
    elements.append(second_table)
    elements.append(Spacer(1, 20))

def generate_pdf_report(bin_similarity_data, candidate_data, output_path):
    """
    Generate a detailed PDF report from the provided JSON data
    
    Args:
        bin_similarity_data (dict): Parsed JSON data from bin_similarity_score.json
        candidate_data (dict): Parsed JSON data from candidate_data.json
        output_path (str): Path where the PDF should be saved
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=15,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=5
    )
    smaller_header_style = ParagraphStyle(
        'SmallerHeaderStyle',
        parent=header_style,
        fontSize=header_style.fontSize - 4  # Slightly smaller font size
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Building the document
    elements = []
    
    # Title
    elements.append(Paragraph("SkiLL Match Summary", title_style))
    
    # Total Candidate Score at top
    total_score = candidate_data['Total_Candidate_Score'] * 100
    total_label, total_color, total_symbol = create_label_box(total_score)
    
    total_score_table = Table([
        ['Total Candidate Score ', f"{total_score:.1f}%", total_label]
    ], colWidths=[6*inch, 1*inch, 1*inch])
    
    total_score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (2, 0), (2, 0), total_color),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('BOX', (2, 0), (2, 0), 1, colors.black),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
    ]))
    
    elements.append(total_score_table)
    #elements.append(Spacer(1, 20))
    
    # Candidate Information with Experience Label
    experience_score = candidate_data['experience'] * 100
    experience_label, experience_color, _ = create_label_box(experience_score)
    
    candidate_info = [
        [Paragraph(f"Name: {candidate_data['name']}", normal_style),
         Paragraph(f"Phone: {candidate_data['phone']}", normal_style)],
        [Paragraph(f"Email: {candidate_data['email']}", normal_style),
        ]
    ]
    
    info_table = Table(candidate_info, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    #elements.append(info_table)
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("Candidate Information", header_style))
    elements.append(Spacer(1, 5))
    name = Paragraph(f"Name: {candidate_data['name']}", normal_style)
    phone = Paragraph(f"Phone: {candidate_data['phone']}", normal_style)
    email = Paragraph(f"Email: {candidate_data['email']}", normal_style)

    elements.append(name)
    elements.append(phone)
    elements.append(email)
    
    # Technical Skills Assessment
    elements.append(Paragraph("Technical Skills Similarities", header_style))
    
    detailed_scores = bin_similarity_data['similarity_scores']['detailed_technical_skills']
    
    # Create score rows with labels
    def create_score_row(label, score):
        score_value = format_score(score)
        label_text, label_color, _ = create_label_box(score_value)
        return [label, f"{score_value:.1f}%", label_text, label_color]
    
    scores_data = [
        create_score_row("Primary Skills Score", detailed_scores['primary_skills'][0]),
        create_score_row("Non-Negotiable Skills Score", detailed_scores['non_negotiable_skills'][0]),
        create_score_row("Negotiable Skills Score", detailed_scores['negotiable_skills'][0]),
        create_score_row("Optional Skills Score", detailed_scores['optional_skills'][0])
    ]
    
    # Create table for scores
    scores_table = Table(
        [[row[0], row[1], row[2]] for row in scores_data],
        colWidths=[3*inch, 1*inch, 1*inch]
    )
    
    # Apply styles to scores table
    table_style = [
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    
    # Add background colors for labels
    for i, row in enumerate(scores_data):
        table_style.append(('BACKGROUND', (2, i), (2, i), row[3]))
        table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
        table_style.append(('BOX', (2, i), (2, i), 1, colors.black))
        table_style.append(('ALIGN', (2, i), (2, i), 'CENTER'))
    
    scores_table.setStyle(TableStyle(table_style))
    elements.append(scores_table)
    elements.append(Spacer(1, 5))
    
    # Other Assessments
    elements.append(Paragraph("Other Similarities", header_style))
    
    other_scores = [
        create_score_row("Domain Knowledge Score", candidate_data['domain_knowledge_score']),
        create_score_row("Notice Period Favourability", candidate_data['notice_period_favourability']),
        create_score_row("Education Score", candidate_data['education_score']),
        create_score_row("Experience Score  ", candidate_data['experience'])
    ]
    
    other_table = Table(
        [[row[0], row[1], row[2]] for row in other_scores],
        colWidths=[3*inch, 1*inch, 1*inch]
    )
    
    table_style = [
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    
    for i, row in enumerate(other_scores):
        table_style.append(('BACKGROUND', (2, i), (2, i), row[3]))
        table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
        table_style.append(('BOX', (2, i), (2, i), 1, colors.black))
        table_style.append(('ALIGN', (2, i), (2, i), 'CENTER'))
    
    other_table.setStyle(TableStyle(table_style))
    elements.append(other_table)
    elements.append(Spacer(1, 5))
    
    # Skill Gap Analysis with Bullets
    """elements.append(Paragraph("Skill Gap Analysis", header_style))
    gap_sections = split_skill_gap_analysis(candidate_data['Skill Gap Analysis'])
    
    for title, content in gap_sections.items():
        elements.append(Paragraph(f"• <b>{title}:</b> {content}", normal_style))
        #elements.append(Paragraph(f"• {content}", normal_style))"""
    


    # Create a new style with left indentation
    right_aligned_smaller_header_style = ParagraphStyle(
        'RightAlignedSmallerHeaderStyle',
        parent=smaller_header_style,
        leftIndent=.20 * inch  # Adjust the indent as needed
    )
    right_aligned_normal_style = ParagraphStyle(
        'RightAlignedNormalStyle',
        parent=normal_style,
        leftIndent=.20 * inch  # Adjust the indent as needed
    )

    elements.append(Paragraph("Skill Gap Analysis", header_style))
    elements.append(Paragraph("Must Have Skills Analysis", right_aligned_smaller_header_style))
    elements.append(Paragraph(candidate_data['Must have skills'], right_aligned_normal_style))
    elements.append(Paragraph("Good to Have Skills Analysis", right_aligned_smaller_header_style))
    elements.append(Paragraph(candidate_data['Good to have skills'], right_aligned_normal_style))
    elements.append(Paragraph("Optional Skills Analysis", right_aligned_smaller_header_style))
    elements.append(Paragraph(candidate_data['Optional Skills'], right_aligned_normal_style))
    #elements.append(Paragraph(candidate_data['Skill Gap Analysis'], normal_style))
    elements.append(Spacer(1, 5))
    
    #elements.append(Spacer(1, 20))
    
    # Score Summary Table with Symbols
    scores_summary = [
        ('Total Score', candidate_data['Total_Candidate_Score'] * 100),
        ('Experience', candidate_data['experience'] * 100),
        ('Primary Skills', format_score(detailed_scores['primary_skills'][0])),
        ('Non-Negotiable', format_score(detailed_scores['non_negotiable_skills'][0])),
        ('Negotiable', format_score(detailed_scores['negotiable_skills'][0])),
        ('Optional Skills', format_score(detailed_scores['optional_skills'][0])),
        ('Domain Knowledge', candidate_data['domain_knowledge_score'] * 100),
        ('Notice Period', candidate_data['notice_period_favourability'] * 100),
        ('Education', candidate_data['education_score'] * 100)
    ]
    
    #generate_score_summary(elements, scores_summary, header_style)
    
    # Legend
    elements.append(Paragraph("Score Legend", header_style))
    legend_data = [
        ['JD - Resume Similarity Score Range', 'Label', 'Meaning'],
        ['60-100%', 'GOOD', 'Good Fit'],
        ['30-59%', 'NEUTRAL', 'Average Fit'],
        ['0-29%', 'POOR', 'Needs Manual Review']
    ]
    
    legend_table = Table(legend_data, colWidths=[3.5*inch, 1*inch, 2*inch])
    legend_style = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (1, 1), (1, 1), colors.green),
        ('BACKGROUND', (1, 2), (1, 2), colors.orange),
        ('BACKGROUND', (1, 3), (1, 3), colors.red),
        ('TEXTCOLOR', (1, 1), (1, 3), colors.white),
    ]
    
    legend_table.setStyle(TableStyle(legend_style))
    elements.append(legend_table)
    
    # Generate PDF
    doc.build(elements)

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)
    
    # Generate output file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_FOLDER_PATH, f"resume_report_{timestamp}.pdf")
    
    try:
        # Load JSON data
        bin_similarity_data = load_json_file(SIMILARITY_JSON_PATH)
        candidate_data = load_json_file(CANDIDATE_JSON_PATH)
        
        # Generate PDF report
        generate_pdf_report(bin_similarity_data, candidate_data, output_file)
        print(f"\nPDF Report generated successfully: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

main()