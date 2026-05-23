import fitz
import os

dir=os.path.dirname(os.path.abspath(__file__))
path=os.path.join(dir,"SLATEFALL_DOSSIER.pdf")

def get_all_sections(pdf_path=path):
    doc=fitz.open(pdf_path)
    full_text=""
    for page in doc:
        full_text+=page.get_text()
    doc.close()

    sections={}
    current_section_num=None
    current_section_name=""
    current_lines=[]

    for line in full_text.split("\n"):
        stripped=line.strip()
        is_section_heading=False
        if stripped.startswith("Section") and len(stripped)<80:
            parts=stripped.split()
            if len(parts)>=2:
                num_str=parts[1].replace(".","").replace(":","")
                if num_str.isdigit():
                    is_section_heading=True

        if is_section_heading:
            if current_section_num is not None:
                sections[current_section_num]={
                    "title":current_section_name,
                    "content":"\n".join(current_lines).strip()
                }
            current_section_name=stripped
            parts=stripped.split()
            current_section_num=int(parts[1].replace(".","").replace(":",""))
            current_lines=[]
        else:
            current_lines.append(line)

    if current_section_num is not None:
        sections[current_section_num]={
            "title":current_section_name,
            "content":"\n".join(current_lines).strip()
        }

    return sections

def get_section_by_id(section_id:int,pdf_path=path):
    sections=get_all_sections(pdf_path)
    if section_id in sections:
        return sections[section_id]
    return None

def get_section_list(pdf_path=path):
    sections=get_all_sections(pdf_path)
    result=[]
    for num,data in sections.items():
        result.append({
            "section_id":num,
            "title":data["title"],
            "preview":data["content"][:150]+"..."
        })
    return result

if __name__=="__main__":
    sections=get_all_sections()
    print(f"sections: {len(sections)}")
    for num,data in sections.items():
        print(f"{num}: {data['title']}")
    sec=get_section_by_id(8)
    if sec:
        print(f"sec8: {sec['title']}")
    else:
        print("sec8: not found")