---
id: EXP-0002
company: Google
role: Software Engineer (SDE-2)
seniority: SDE-2 (candidate reports 4 years of experience, at a mid-size tech company)
format: Reported as 5 rounds (1 phone screen, 3 technical on-site, 1 behavioral); only 4 rounds are described in the text
interview_date: January 15, 2025 (as reported; unclear whether this is one round or the whole process)
location: Bangalore, India
source: Text file attached by user on 2026-10-16. Original author, platform and URL: Unknown.
outcome: Unknown (not reported)
process_duration: About 3 weeks from first recruiter call to final decision (reported)
ingested: 2026-10-16
notes: Source text contains "&lt;" where the code meant "<" (HTML escaping), preserved verbatim below. Candidate's solutions were in Python.
---

# Raw experience (verbatim)

Candidate Information
Status: Software Engineer with 4 years of experience, currently employed at a mid-size tech company

Target Position: Software Engineer (SDE-2) at Google

Location: Bangalore, India

Interview Date: January 15, 2025

Overview of Interview Process

The Google interview process for SDE-2 consisted of 5 rounds: one phone screening, three technical on-site rounds, and one behavioral round. The entire process took about 3 weeks from the initial recruiter call to the final decision.

Round 1: Phone Screening (45 minutes)

Duration: 45 minutes

Method: Google Meet with shared Google Doc for coding

Focus: Data Structures and Algorithms

The interviewer was friendly and started with a brief introduction. After a short discussion about my background, we moved to a coding problem.

Coding Problem 1: Two Sum with Sorted Array Pairs

Problem: Given a sorted array of integers and a target sum, find all unique pairs of elements that add up to the target. Return the pairs in ascending order.

Example:

Input: arr = [1, 2, 3, 4, 5, 6, 7], target = 8

Output: [[1,7], [2,6], [3,5]]

My Approach: I used the two-pointer technique since the array is already sorted. I placed one pointer at the beginning and one at the end, then moved them inward based on whether the current sum was less than or greater than the target.

Solution (Python):

def find_pairs(arr, target):

result = []

left, right = 0, len(arr) - 1

while left &lt; right:

current_sum = arr[left] + arr[right]

if current_sum == target:

result.append([arr[left], arr[right]])

left += 1

right -= 1

while left &lt; right and arr[left] == arr[left - 1]:

left += 1

while left &lt; right and arr[right] == arr[right + 1]:

right -= 1

elif current_sum &lt; target:

left += 1

else:

right -= 1

return result

Time Complexity: O(n) where n is the length of the array.

Space Complexity: O(1) excluding the output array.

The interviewer was satisfied with the solution and asked a follow-up about handling duplicates, which was already addressed in my code.

Round 2: Technical On-site Round 1 (45 minutes)

Duration: 45 minutes

Method: In-person at Google Bangalore office

Focus: Trees and Graph Algorithms

Coding Problem 2: Lowest Common Ancestor in a Binary Tree

Problem: Given a binary tree and two nodes p and q, find their lowest common ancestor (LCA). The LCA is the deepest node that is an ancestor of both p and q.

My Approach: I used a recursive DFS approach. If we find either p or q in a subtree, we return that node. If both left and right recursive calls return non-null values, the current node is the LCA.

Solution (Python):

class TreeNode:

def __init__(self, val=0, left=None, right=None):

self.val = val

self.left = left

self.right = right

def lowest_common_ancestor(root, p, q):

if root is None or root == p or root == q:

return root

left = lowest_common_ancestor(root.left, p, q)

right = lowest_common_ancestor(root.right, p, q)

if left and right:

return root

return left if left else right

Time Complexity: O(n) where n is the number of nodes.

Space Complexity: O(h) where h is the height of the tree.

The interviewer asked a follow-up about optimizing for a BST. I explained we could compare values with root to determine which subtree to search.

Round 3: System Design (45 minutes)

This round focused on designing a URL shortening service. I discussed hashing strategy, database schema, caching with Redis, and handling high read throughput.

Round 4: Behavioral Round (30 minutes)

Questions about handling disagreements, making decisions with incomplete information, and mentoring junior engineers. I used the STAR method for structured answers.

Tips for Preparation

Practice coding on a Google Doc without IDE auto-completion

Focus on explaining your thought process clearly while coding

Study graph algorithms, dynamic programming, and tree problems thoroughly

For system design, practice designing scalable distributed systems

Prepare behavioral stories using the STAR method