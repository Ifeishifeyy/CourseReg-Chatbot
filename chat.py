import json
import random
import torch
import re
from model import NeuralNet
from datetime import datetime
from nltk_utils import bag_of_words, tokenize


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

with open('courses.json', 'r') as f:
    courses = json.load(f)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "bot"

def get_response(msg, program, level, option=None):
    # Clean up program/option values
    program = program.lower() if program else None
    
    # Handle Industrial Mathematics with options
    if program == "industrial mathematics" and option:
        option = option.lower()
        if option == "computer science":
            option = "Computer Science"  # Consistent naming
        elif option == "pure":
            option = "Pure"
        elif option == "statistics":
            option = "Statistics"

    if option == "computer science":
            # Ensure we're using the correct program/option combination
            program = "industrial mathematics"
            option = "Computer Science"  # Consistent naming

    """ Returns course recommendations or general responses. """
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    program = extractProgram(msg, program)  # Pass the current program

# Special case: If Industrial Mathematics needs option selection
    if program and program.lower() == "industrial mathematics" and option is None:
            return {
                "response": "Please specify your option in Industrial Mathematics:",
                "buttons": [
                    {"label": "Pure", "value": "Pure"},
                    {"label": "Statistics", "value": "Statistics"},
                    { "label": "Computer Science (Maths)", "value": "Computer Science" }
                ]
        }

    # Existing response handlers (now returning dicts when buttons are needed)
    if any(word in msg.lower() for word in ["tell me ", "what is", "what","details about", "explain","brief","expantiate"]) and "about" in msg.lower() and not any(excluded in msg.lower() for excluded in ["carryover", "carry over"]):
        response = get_course_details(msg, program, level, option)
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["probation","probating","probate"]):
        response = probation()
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["prerequisites", "prerequisite", "prerequisites","prerequisities", "prerequisties"])and any(unit_word in msg.lower() for unit_word in ["fail", "did not pass", "failed", "do not pass","banged", "bang"]):
        return {"response": get_prerequisite_failure_policy()}
    
    if any(word in msg.lower() for word in ["gradation requirement", "graduation requirements", "graduation requirement", "convo requirements", "convocation requirements", "convocation requirement", "graduation", "convo"]):
        response = graduation_requirements(program,option)
        return {"response": response} if isinstance(response, str) else response

    if any(word in msg.lower() for word in ["prerequisites", "prerequisite", "prerequisites", "prerequisite","prerequisities", "prerequisties"]) and ("of" in msg.lower() or "for" in msg.lower()) and not any(excluded in msg.lower() for excluded in ["fail", "did not pass", "failed", "do not pass","banged", "bang"]):
        response = get_prerequisite(msg, program, level, option)
        return {"response": response} if isinstance(response, str) else response

    if any(word in msg.lower() for word in ["max number","maximum number","highest number","maximum"]) and any(unit_word in msg.lower() for unit_word in ["credit", "credits", "units", "unit"]):
        response = maxNumofUnits()
        return {"response": response} if isinstance(response, str) else response

    if any(word in msg.lower() for word in ["units", "credits", "unit", "credit"]):
        response = get_units_offered(program, level, option)
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["how many","number","how much"]) and ("course","courses" in msg.lower()) and not any(excluded in msg.lower() for excluded in [ "elective","electives"]):
        response = get_total_courses_offered(program, level, option)
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["how many","number"]) and ("electives","elective" in msg.lower()):
        response = get_elective_count(program, level, option)
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["elective outside", "electives outside", "external electives", "cross-department", "other departments","another department"
                                        "other department"]) or "outside my department" in msg.lower():
        return {"response": get_elective_outside_department_policy()}
    
    if any(word in msg.lower() for word in ["what", "doing", "offering","list"]) and any(course_word in msg.lower() for course_word in ["courses", "course"]):
        response = get_courses_offered(program, level, option)
        return {"response": response } if isinstance (response,str) else response
    
    if any(word in msg.lower() for word in ["easy", "easiest", "simple", "simplest","sure A", "sure A's", "easy A","not difficult"]) and ("courses", "course", "elective","electives" in msg.lower()):
        response = easyCourses()
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["still need","still do","should i","siwes","it","i.t.","i.t", "internship", "industrial training","must i","can i not do"]) \
        and any(keyword in msg.lower() for keyword in ["course reg", "course registration", "registration", "reg"]):
            response = "Every student needs to complete your course registration through the school's official portal."
            return {"response": response} if isinstance(response, str) else response

    if any(word in msg.lower() for word in ["how to reset","how can I reset","is it possible to reset","is it possible to do","can I reset","can I redo","reset","redo"]) and any(keyword in msg.lower() for keyword in ["course", "courses", "course registration","course reg"]):
        response = reset_course_registration()
        return {"response": response} if isinstance(response, str) else response

    if any(word in msg.lower() for word in ["carryover", "carry over courses", "failed courses","courses I failed", "carry over", "carryover courses","carry-over"]):
        response = carryOver(level)
        return {"response": response} if isinstance(response, str) else response
    
    if any(word in msg.lower() for word in ["course structure", "structure", "program structure", "course structure", "curriculum structure"]):
        response = get_course_structure()
        return {"response": response} if isinstance(response, str) else response

    if any(phrase in msg.lower() for phrase in ["how to register", "how do i register", "how do i do","how do", "how to","how am I to"]) \
        and not any(excluded in msg.lower() for excluded in ["reset", "carryover", "carry over"]) \
        and any(keyword in msg.lower() for keyword in ["course", "courses", "registration"]):
            response = courseReg_how()
            return {"response": response} if isinstance(response, str) else response

    if program and level:
        career_choice = extract_career_choice(msg)
        if career_choice:
            response = recommend_electives(program, level, career_choice, option=option)
            return {"response": response} if isinstance(response, str) else response
        else:
            response = recommend_electives(program, level, option=option)
            return {"response": response} if isinstance(response, str) else response
    
    if program and not level:
        return {
            "response": f"Got it! You are studying {program}. Now, please tell me your level (e.g., 100, 200, 300, 400).",
            "buttons": [
                {"label": "100 Level", "value": "100"},
                {"label": "200 Level", "value": "200"},
                {"label": "300 Level", "value": "300"},
                {"label": "400 Level", "value": "400"}
            ]
        }
    

    if prob.item() > 0.5:
        if tag == "elective_recommendation":
            if program and level:
                response = recommend_electives(program, level, option=option)
                return {"response": response} if isinstance(response, str) else response
            else:
                return {"response": "Please specify your program and level to get course recommendations."}
        elif tag == "prerequisite_query":
            response = get_prerequisite(msg, program, level, option)
            return {"response": response} if isinstance(response, str) else response
        elif tag == "course_details":
            response = get_course_details(msg, program, level, option)
            return {"response": response} if isinstance(response, str) else response
        elif tag == "units_offered":
            response = get_units_offered(program, level, option)
            return {"response": response} if isinstance(response, str) else response
        elif tag == "elective_count":
            response = get_elective_count(program, level, option)
            return {"response": response} if isinstance(response, str) else response
        elif tag == "prerequisite_failure":
            return {"response": get_prerequisite_failure_policy()}
        elif tag == "courses_offered":
            response = get_courses_offered(program, level, option)
            return {"response": response} if isinstance(response, str) else response
        elif tag == "elective_outside_department":
            return {"response": get_elective_outside_department_policy()}
        elif tag == "easyCourses":
            return {"response":easyCourses()}
        elif tag == "resetCourseReg":
            return {"response": reset_course_registration()}
        elif tag == "carryover":
            return {"response": carryOver(level)}
        elif tag == "maxUnits":
            return {"response":maxNumofUnits}
        else:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    return {"response": random.choice(intent['responses'])}

    return {"response": "I do not understand. Can you rephrase?"}

def get_current_semester():
    month = datetime.now().month
    return "Alpha" if month <= 2 else "Omega"

def extract_course_code(text):
    matches = re.findall(r'([A-Za-z]{2,})\s?(\d{3})', text)
    return [code[0].upper() + code[1] for code in matches]


def recommend_electives(program, level,career_choice=None,option=None):
    semester = get_current_semester()
    electives = []

    if level == "100":
        return "No electives for 100 level students."
    
    if level == "300" and semester == "Omega":
        return "No electives for SIWES students."
    
    program = next((p for p in courses if p.lower() == program.lower()), program)
    if program == "Industrial Mathematics" and option:
            if option in courses[program]:
                if "electives" in courses[program][option] and level in courses[program][option]["electives"]:
                    if semester in courses[program][option]["electives"][level]:
                        electives = courses[program][option]["electives"][level][semester]
            else:
            # If no option is specified, return a message asking for the option
                return "Please specify a valid option (e.g., Pure, Statistics, or Computer Science) to get elective recommendations."
    else:        
        if program in courses and "electives" in courses[program]:
            if level in courses[program]["electives"] and semester in courses[program]["electives"][level]:
                electives = courses[program]['electives'][level][semester]

    if career_choice:
        recommended_electives = []
        # Check each elective's career relevance
        for elective_code in electives:
            course_list = courses[program][option]["courses"] if program == "Industrial Mathematics" and option and "courses" in courses[program][option] else courses[program]["courses"]
            for course in course_list:
                if course["code"] == elective_code:
                    if any(career_choice.lower() == cr.lower() for cr in course.get("career_relevance", [])):
                        recommended_electives.append(f"{course['code']} - {course['title']}")

            if recommended_electives:
                return (
                    f"Based on your career choice, here are the best electives for you:\n"
                    f"{'\n'.join(recommended_electives)}"
                )
            else:
                return f"No electives found that align with your career choice ({career_choice}).While no electives specifically align with your career choice, consider choosing an elective that interests you personally. I can provide you with more information about the available electives if you'd like."
    else:
            # Return all electives if no career choice is provided
            elective_list = "\n".join(electives)
            return (
                f"The electives available for {program}-({option}) students in {semester} semester, {level} level are:\n"
                f"{elective_list}\n\n"
                "Do you have a specific career choice in mind? (e.g., Data Science, Software Engineering, etc.) "
             )
    return "No electives found for your selection."       

def courseReg_how():
    return "How to Do Your Course Registration:\n\n1. Log in to your student portal using your registration number as your username and your password.\n\n2. Navigate to the “Course Control” section.\n\n3. Ensure the sidebar is visible, then click on “Course Registration.”\n\n4. From the dropdown menu, select “Do Semester Registration.”\n\n5. Choose the courses you intend to offer for the semester and submit them for approval.\n\n6.Once submitted, print a copy of your course form and submit it to your level advisor for final clearance."

def maxNumofUnits():
    return "The maximum number of units a student shall be allowed to register per semester is 25 units while the minimum is 15 units."

def carryOver(level):
    if level == "100":
        return "Carryover courses are not applicable to 100 level students."
    else:
        return "At the point of course registration, all previously failed or dropped courses must be registered first. Carryover courses should be registered alongside other courses in accordance with standard registration procedures. Please note that carryover courses from the Alpha semester must be registered and taken exclusively during the Alpha semester, and similarly, carryover courses from the Omega semester must be registered and taken only during the Omega semester."
def probation():
    return "Probation is assigned to students whose academic performance is below acceptable standards. A student with a CGPA between 1.0 and 1.49 is considered Not in Good Standing (NGS) and can remain at the same course level to retake failed courses, while retaining passed ones. A student with a Cumulative Grade Point Average (CGPA) below 1.0 at the end of their first session must withdraw from the program. Additionally, a student on probation whose CGPA falls below 1.5 at the end of the year shall be required to withdraw from the University. They may also register for any outstanding dropped courses. Note that a student cannot be on probation more than once. "

def reset_course_registration():
    return "You can reset your course registration provided it is still within the registration period. \n\n How to Reset Your Course Registration:\n\n1. Log in to your student portal using your registration number as your username and your password.\n\n2. Navigate to the “Course Control” section.\n\n3. Ensure the sidebar is visible, then click on “Course Registration.”\n\n4. From the dropdown menu, select “Do Course Registration Reset”\n\n5. Choose the courses you intend to offer for the semester and submit them for approval.\n\n6.Once submitted, print a copy of your course form and submit it to your level advisor for final clearance"

def get_prerequisite(course_name, program, level, option):
    try:
        # Normalize the program name
        program = next((p for p in courses if p.lower() == program.lower()), program)
        program = program.title()

        course_codes = extract_course_code(course_name)

        if not course_codes:
            return "Please provide a valid course code."

        results = []

        def find_course(code):
            # Search in Industrial Mathematics with option
            if program == "Industrial Mathematics" and option:
                opt_data = courses.get(program, {}).get(option.title(), {})
                for course in opt_data.get("courses", []):
                    if course["code"].upper() == code:
                        return course

            # Search in regular programs
            if program in courses and "courses" in courses[program]:
                for course in courses[program]["courses"]:
                    if course["code"].upper() == code:
                        return course

            # Global fallback: check all courses
            for prog_data in courses.values():
                if "courses" in prog_data:
                    for course in prog_data["courses"]:
                        if course["code"].upper() == code:
                            return course
                else:  # Programs with options
                    for opt_data in prog_data.values():
                        for course in opt_data.get("courses", []):
                            if course["code"].upper() == code:
                                return course
            return None

        for code in course_codes:
            course = find_course(code)
            if course:
                if "prerequisites" in course and course["prerequisites"]:
                    results.append(f"⏪ Prerequisites for {code}: {', '.join(course['prerequisites'])}")
                else:
                    results.append(f"✅ {code} has no prerequisites.")
            else:
                results.append(f"⚠️ Course {code} not found.")

        return "\n".join(results)

    except Exception as e:
        print(f"Error in get_prerequisite: {str(e)}")
        return "Sorry, I encountered an error while retrieving prerequisites."

def extractProgram(text, current_program=None):
    lowerText = text.lower()
    
    # Never change from Industrial Mathematics if that's our current program
    if current_program and current_program.lower() == "industrial mathematics":
        return current_program
        
    # Normal program detection
    if "industrial mathematics" in lowerText or "maths" in lowerText or "mathematics" in lowerText:
        return "Industrial Mathematics"
    elif "computer science" in lowerText or "cs" in lowerText:
        return "Computer Science"
    
    return current_program
def get_course_details(course_name, program, level, option):
    try:
        program = program.title() if program else None
        course_name = course_name.lower().strip()

        course_codes = extract_course_code(course_name)

        if not course_codes:
            return "Please provide a valid course code."
        
        results = []

        # Helper function to search for a course
        def find_course(code):
            # Search in program with options
            if program == "Industrial Mathematics" and option:
                opt_data = courses.get(program, {}).get(option.title(), {})
                for course in opt_data.get("courses", []):
                    if course["code"].upper() == code:
                        return course

            # Search in regular programs
            if program in courses:
                for course in courses[program].get("courses", []):
                    if course["code"].upper() == code:
                        return course

            # Global fallback
            for prog_data in courses.values():
                if "courses" in prog_data:
                    for course in prog_data["courses"]:
                        if course["code"].upper() == code:
                            return course
                else:  # Programs with options
                    for opt_data in prog_data.values():
                        if "courses" in opt_data:
                            for course in opt_data["courses"]:
                                if course["code"].upper() == code:
                                    return course
            return None

        # Loop through each detected course code and get details
        for code in course_codes:
            course = find_course(code)
            if course:
                results.append(format_course_details(course))
            else:
                results.append(f"⚠️ Course {code} not found.")

        if results:
            return "\n\n".join(results)
        else:
            return "No valid course codes found in your message."

    except Exception as e:
        print(f"Error in get_course_details: {str(e)}")
        return "Sorry, I encountered an error while searching for the course details."

def format_course_details(course):
    details = [
        f"📚 {course['code']} - {course['title']}",
        f"📝 Description: {course['description']}",
        f"📊 Units: {course['credits']}",
        f"📅 Level: {course['level']}",
        f"🏛️ Type: {'Compulsory' if course['type'] == 'C' else 'Elective'}",
        f"🎯 Career Relevance: {', '.join(course['career_relevance'])}"
    ]
    if course['prerequisites']:
        details.append(f"⏪ Prerequisites: {', '.join(course['prerequisites'])}")
    return '\n'.join(details)
def extract_career_choice(msg):
    career_keywords = {
        "data scientist": ["data science", "data scientist", "data engineer"],
        "statistician": ["statistician","survey statistician"],
        "AI engineer": ["artificial intelligence", "ai engineer", "ai specialist", "ai researcher","AI/ML engineer"],
        "machine learning engineer": ["ML engineer","machine learning engineer"],
        "data analyst": ["data analysis", "data analyst", "data analytics"],
        "software engineer": ["software engineering", "software engineer", "software developer"],
        "web developer": ["web development", "web developer", "frontend developer", "full-stack developer"],
        "mathematician": ["mathematician"],
        "Actuary":["actuary"],
        "Cryptographer": ["cryptographer", "cryptography"],
        "academic researcher": ["academic research", "research scientist", "researcher","lecturer"],
        "network engineer": ["networking", "network engineer", "network administrator", "network architect","network security engineer"],
        "engineer": ["engineering", "computer engineering", "embedded systems engineer","engineer"],
        "animator": ["animator","3D animator","2D animator","3D artist","2D artist","3D Generalist"],
        "project manager": ["project manager","project management", "project manager", "IT project manager"],
        "business analyst": ["business analysis","business analytics" ,"business analyst", "business intelligence analyst","BI analyst"],
        "operations research analyst": ["operations research", "operations research analyst"],
        "system administrator": ["system administration", "systems analyst", "system administrator"],
        "game developer": ["game development", "game developer","game programmer",],
        "bioinformatics specialist": ["bioinformatics", "computational biologist", "bioinformatics specialist"],
        "simulation engineer": ["simulation", "simulation engineer"],
        "cloud architect": ["cloud computing", "cloud architect", "distributed systems engineer"],
        "database administrator": ["database administration", "database administrator"],
        "cybersecurity specialist": ["cybersecurity", "cybersecurity specialist","cybersecurity expert","security specialist", "penetration tester","cybersecurity analyst"],
        "performance engineer": ["performance engineering", "performance engineer"],
        "quality control analyst": ["quality control", "quality control analyst","quality control engineer"],
        "hardware engineer": ["hardware engineering", "hardware engineer"],
        "it consultant": ["it consulting", "it consultant","IT Support Specialist"],
        "supply chain analyst": ["supply chain", "supply chain analyst"],
        "UI/UX designer": ["UI/UX designer", "UI designer", "UX designer"],
        "accountant": ["accounting", "accountant"]
    }
    
    for career, variations in career_keywords.items():
        if any(variation in msg.lower() for variation in variations):
            return career
    return None
def extract_option(msg, program=None):
    msg = msg.lower()
    if program and program.lower() != "industrial mathematics":
        return None
        
    if program == "Industrial Mathematics":
        if re.search(r'\bcomputer science\b|\bcs\b', msg):
            return "Computer Science"  # Consistent naming
        elif re.search(r'\bpure\b', msg):
            return "Pure"
        elif re.search(r'\bstatistics\b', msg):
            return "Statistics"
    return None

def get_elective_limit(program, level, semester, option=None):
    elective_limits = {
        "Industrial Mathematics": {
            "Computer Science": {
                "100": {"Alpha": 0, "Omega": 0},
                "200": {"Alpha": 1, "Omega": 1},
                "300": {"Alpha": 1, "Omega": 0},
                "400": {"Alpha": 2, "Omega": 1}
            },
            "Pure": {
                "100": {"Alpha": 0, "Omega": 0},
                "200": {"Alpha": 1, "Omega": 1},
                "300": {"Alpha": 1, "Omega": 0},
                "400": {"Alpha": 2, "Omega": 1}
            },
            "Statistics": {
                "100": {"Alpha": 0, "Omega": 0},
                "200": {"Alpha": 1, "Omega": 1},
                "300": {"Alpha": 1, "Omega": 0},
                "400": {"Alpha": 2, "Omega": 1}
            }
        },
        "Computer Science": {
            "100": {"Alpha": 0, "Omega": 0},
            "200": {"Alpha": 1, "Omega": 2},
            "300": {"Alpha": 2, "Omega": 0},
            "400": {"Alpha": 1, "Omega": 1}
        },
        "MIS": {
            "100": {"Alpha": 0, "Omega": 0},
            "200": {"Alpha": 1, "Omega": 1},
            "300": {"Alpha": 1, "Omega": 0},
            "400": {"Alpha": 1, "Omega": 1}
        }
    }

    try:
        program = next((p for p in elective_limits if p.lower() == program.lower()), program)
        level = str(level)
        semester = semester.capitalize()

        if program == "Industrial Mathematics" and option:
            option = option.title()
            return elective_limits.get(program, {}).get(option, {}).get(level, {}).get(semester, 0)
        else:
            return elective_limits.get(program, {}).get(level, {}).get(semester, 0)
    except Exception as e:
        print(f"Error in get_elective_limit: {str(e)}")
        return 0  # fallback if anything goes wrong


def get_total_courses_offered(program, level, option=None):
    semester = get_current_semester().lower()
    total_courses = 0
    elective_courses = []

    try:
        program = next((p for p in courses if p.lower() == program.lower()), program)
        level = str(level)

        if not program or not level:
            return "Please provide both your program and level."

        elective_limit = get_elective_limit(program, level, semester, option)

        if program == "Industrial Mathematics" and option:
            option = option.title()
            course_list = courses[program][option]["courses"]
        else:
            course_list = courses[program]["courses"]

        for course in course_list:
            if str(course.get("level")) == level and course.get("semester").lower() == semester:
                course_type = course.get("type", "C")
                if course_type == "E":  # Elective
                    elective_courses.append(course)
                else:
                    total_courses += 1

        total_courses += min(elective_limit, len(elective_courses))

        if total_courses > 0:
            return f"You are offering {total_courses} courses this semester."
        else:
            return f"No courses found for {program}{f' ({option})' if option else ''} in {semester.capitalize()} semester, {level} level."

    except Exception as e:
        print(f"Error in get_total_courses_offered: {str(e)}")
        return "Sorry, I encountered an error while checking your courses."


def get_total_units(program, level, semester, option=None):
    program = next((p for p in courses if p.lower()==program.lower()), program)
    level = str(level)
    semester = semester.capitalize()

    units = {
        "Industrial Mathematics": {
            "Computer Science": {
                "100": {"Alpha": 24, "Omega": 23},
                "200": {"Alpha": 23, "Omega": 23},
                "300": {"Alpha": 22, "Omega": 6},
                "400": {"Alpha": 23, "Omega": 21}
            },
            "Pure": {
                "100": {"Alpha": 24, "Omega": 24},
                "200": {"Alpha": 22, "Omega": 22},
                "300": {"Alpha": 23, "Omega": 6},
                "400": {"Alpha": 23, "Omega": 23}
            },
            "Statistics": {
                "100": {"Alpha": 24, "Omega": 22},
                "200": {"Alpha": 21, "Omega": 23},
                "300": {"Alpha": 24, "Omega": 6},
                "400": {"Alpha": 23, "Omega": 23}
            }
        },
        "Computer Science": {
                "100": {"Alpha": 24, "Omega": 23},
                "200": {"Alpha": 24, "Omega": 23},
                "300": {"Alpha": 24, "Omega": 6},
                "400": {"Alpha": 21, "Omega": 23}
        },
        "MIS":{
                "100": {"Alpha": 21, "Omega": 24},
                "200": {"Alpha": 19, "Omega": 22},
                "300": {"Alpha": 25, "Omega": 6},
                "400": {"Alpha": 17, "Omega": 21}
            }
        }

    program_limits = units.get(program, {})
    
    if isinstance(program_limits, dict):
        if any(isinstance(v, dict) and level in v for v in program_limits.values()):
            # Option must be provided for nested programs
            if option and option.title() in program_limits:
                return program_limits[option.title()].get(level, {}).get(semester, 0)
            else:
                return 0
        else:
            # Program is flat (e.g., Computer Science or MIS)
            return program_limits.get(level, {}).get(semester, 0)

    return 0  # fallback

def get_units_offered(program, level, option):
    semester = get_current_semester().capitalize() 
    program = next((p for p in courses if p.lower()==program.lower()), program)

    # Get elective limit using the new helper
    total_units = get_total_units(program, level, semester, option)
    if total_units > 0:
         # Use title case for display
        program_display = program.title() if program else "your program"
        option_display = f" ({option.title()})" if option else ""
        level_display = str(level) if level else ""

        # Specific check for SIWES semester (where units might be low, e.g., 6)
        if level == "300" and semester.capitalize() == "Omega" and total_units == 6:
             return f"You are on SIWES this semester, which is {total_units} units."

        return f"You are offering {total_units} units this {semester} semester."
    else:
         # Handle cases where lookup returned 0 or program/level/semester combo wasn't found
         return f"I couldn't find the predefined unit information for your Program."

   
def get_elective_count(program, level, option=None):
    semester = get_current_semester().capitalize()

    try:
        program = next((p for p in courses if p.lower() == program.lower()), program)
        level = str(level)

        if level == "100":
            return "No electives for 100 level students."

        # Get elective limit using the new helper
        elective_limit = get_elective_limit(program, level, semester, option)

        # Count available electives
        if program == "Industrial Mathematics" and option:
            option = option.title()
            available_electives = len(courses[program][option]["electives"][level][semester])
        else:
            available_electives = len(courses[program]["electives"][level][semester])

        if elective_limit is not None:
            return f"You can choose from {available_electives} elective(s) this semester. You are to offer only {elective_limit} elective(s) this semester."
        else:
            return f"I couldn't find elective information for {program} {level} level in the {semester} semester."

    except Exception as e:
        print(f"Error in get_elective_count: {str(e)}")
        return "Sorry, I encountered an error while checking your electives. Please make sure you've selected your program and level correctly."

def get_prerequisite_failure_policy():
    return "Covenant University does not implement the prerequisite system so if you fail a prequisite course you are still eligible to do the next course. Please consult your academic advisor for further information."

def easyCourses():
    return "That really depends on your interests and strengths! Generally, electives that align with your natural skills or hobbies tend to be easier. You can ask seniors for tips on which courses are more manageable. Remember, the goal is to learn and grow, not just to get an easy grade!"

def get_course_structure():
    return "You can get your course structure from the student portal. \n\n How to Get Your Course Structure:\n\n1. Log in to your student portal using your registration number as your username and your password.\n\n2. Navigate to the “Course Control” section.\n\n3. Ensure the sidebar is visible, then click on “Course Structure.”\n\n4. From the dropdown menu, select “View Student Course Structure”.\n\n5. You will see your course structure, including all the courses you need to take for your program.\n\n You can print or save this information for your reference."

def graduation_requirements(program, option=None):
    program = next((p for p in courses if p.lower() == program.lower()), program).lower()
    option = option.lower() if option else None

    requirements = {
        "computer science": "The graduation requirement for Computer Science:\n• 168 total units\n• No outstanding carryovers",
        "mis": "The graduation requirement for MIS:\n • 155 total units\n• No outstanding carryovers",
        "industrial mathematics": {
            "computer science": "The graduation requirement for Industrial Mathematics (Computer Science):\n• 165 total units\n• No outstanding carryovers",
            "pure": "The graduation requirement for Industrial Mathematics (Pure):\n• 167 total units\n• No outstanding carryovers",
            "statistics": "The graduation requirement for Industrial Mathematics (Statistics):\n• 166 total units\n• No outstanding carryovers"
        }
    }

    if program == "industrial mathematics":
        if option:
            return requirements[program].get(option, "Please specify a valid option (Pure, Statistics, Computer Science).")
        else:
            return "Please specify your option (Pure, Statistics, Computer Science) for Industrial Mathematics."
    else:
        return requirements.get(program, "Contact your department for graduation requirements.")

def get_courses_offered(program, level, option):
    semester = get_current_semester()
    course_groups = {
        "C": {"name": "COMPULSORY COURSES", "courses": []},
        "E": {"name": "ELECTIVE COURSES", "courses": []},
        "U": {"name": "UNIVERSITY COURSES", "courses": []},
        "V": {"name": "VALUE-BASED COURSES", "courses": []},
        "S": {"name": "SIWES","courses":[]}
    }
    offered_courses = []

    try:
        program = program.title() if program else None
        level = str(level)  # Ensure level is string for comparison

        program = next((p for p in courses if p.lower()==program.lower()), program)

        if not program or not level:
            return "Please provide both your program and level to check the courses offered."
        
        if program == "Industrial Mathematics" and option:
            option = option.title()
            if program in courses and option in courses[program] and "courses" in courses[program][option]:
                for course in courses[program][option]["courses"]:
                    if str(course.get("level")) == level and course.get("semester").lower() == semester.lower():
                        course_info = f"{course['code']} - {course['title']}"
                        course_type = course.get("type", "C")
                        if course_type in course_groups:
                            course_groups[course_type]["courses"].append(course_info)

        elif program in courses and "courses" in courses[program]:
            for course in courses[program]["courses"]:
                if str(course.get("level")) == level and course.get("semester").lower() == semester.lower():
                    course_info = f"{course['code']} - {course['title']}"
                    course_type = course.get("type", "C")
                    if course_type in course_groups:
                        course_groups[course_type]["courses"].append(course_info)

        response = []
        if any(course_group["courses"] for course_group in course_groups.values()):
            response.append(f"Here are the courses you are offering this semester: ")
            
            for course_type in ["C", "E", "U", "V","S"]:  # Maintain this order in output
                group = course_groups[course_type]
                if group["courses"]:
                    response.append(f"\n{group['name']}:")
                    response.extend([f"• {course}" for course in group["courses"]])
            
            return "\n".join(response)
        else:
            return f"No courses found for {program}{f' ({option})' if option else ''} in {semester} semester, {level} level."
    except Exception as e:
        print(f"Error in get_courses_offered: {str(e)}")
        return "Sorry, I encountered an error while checking your courses. Please make sure you've selected your program and level correctly."

def get_elective_outside_department_policy():
    return "Taking electives outside your department is generally allowed, but it depends on course availability and departmental policies. Please consult your academic advisor for specific guidance."


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break
        response = get_response(sentence)
        print(response)
