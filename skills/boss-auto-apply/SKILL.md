---
name: boss-auto-apply
description: Use this skill whenever the user asks Codex to operate Boss/BOSS直聘 for job search, automated applications, "立即沟通", HR chat, or "帮我投递 N 家", especially when they mention cli-anything-pyautogui, 测试开发工程师, 软件测试, 测试工程师, AI大模型应用开发, or other岗位关键词. This skill drives the already-open Boss UI with cli-anything-pyautogui, searches from the user's role terms, skips previously contacted jobs, completes the two-step 立即沟通 flow, sends exactly one customized HR message based on the user's prompt and visible JD, and reports completed/failed applications.
---

# Boss Auto Apply

Use this skill to automate a user-authorized Boss 直聘 job application flow through the visible desktop UI. The user should already have Boss open in a browser or app and be using an account they are allowed to operate.

The goal is practical completion: search for the requested role, open relevant jobs, click the two `立即沟通` steps, enter the chat page, send one tailored message, and count that as one completed application.

## Required Tooling

Drive the UI with `cli-anything-pyautogui` by default. Use browser DOM tooling only as a fallback when the user explicitly asks for it or when screenshots alone cannot resolve the page state.

Useful commands:

```powershell
cli-anything-pyautogui --json status
cli-anything-pyautogui --json screenshot <path>
cli-anything-pyautogui --json click <x> <y>
cli-anything-pyautogui write "<message>"
cli-anything-pyautogui key press enter
cli-anything-pyautogui scroll <clicks> --x <x> --y <y>
cli-anything-pyautogui hotkey ctrl l
cli-anything-pyautogui hotkey alt left
```

Keep screenshot files in a temporary or clearly named path such as `E:\boss-auto-apply-current.png`, and overwrite or rotate them only as needed for inspection.

## Inputs To Extract

Before acting, infer these from the user's prompt and current conversation:

- Target count: how many companies/jobs to apply to.
- Role keywords: for example `测试开发工程师`, `软件测试`, `Java 测试开发`, `自动化测试`.
- Chat instruction: the user's preferred message style or points to emphasize.
- Hard constraints: city, salary, seniority, industry, remote/on-site preference, or companies to avoid.

If the target count is missing, default to one application. If role keywords are missing, use the most recent role terms in the conversation. If no role terms are available, ask a short clarification before operating.

## State Tracking

Maintain a small working list while operating:

- `completed`: company, job title, recruiter, and search keyword for each successfully messaged job.
- `skipped_already_contacted`: jobs that appear previously applied/contacted.
- `failed`: jobs blocked by verification, ambiguous resume choice, missing controls, or unrelated content.

Do not re-apply to anything in `completed` or `skipped_already_contacted`. Also treat a job as already contacted when the visible UI shows signs such as `继续沟通`, `已沟通`, `沟通过`, `已投递`, an existing chat with the same company/recruiter/job, or the current conversation history indicates this job/company was already completed. A normal popup saying `已向BOSS发送消息` immediately after clicking a fresh `立即沟通` is not by itself a duplicate; continue into chat only if the job was not already marked as contacted.

## Operating Workflow

1. Inspect the current UI.
   - Run `cli-anything-pyautogui --json status`.
   - Take a screenshot and read the visible state.
   - Confirm Boss is open and logged in from the UI. If Boss is not open, not logged in, blocked by QR/captcha, or not visible enough to operate, record a failure reason instead of guessing.

2. Search using the user's role keywords.
   - Prefer the Boss search box if visible.
   - Use `hotkey ctrl l` only when the current page URL/search flow clearly supports navigation or search field focus; otherwise click the visible search input.
   - Type the role keywords with `write`, submit with Enter, and wait briefly before taking another screenshot.

3. Choose matching jobs.
   - Pick jobs whose visible title or JD is related to the requested role.
   - Favor stronger matches over first-visible results when the screenshot makes the distinction clear.
   - Avoid jobs that are visibly unrelated, already rejected, already communicated, expired, blocked, or already present in the working state.
   - Before clicking `立即沟通`, inspect the selected job's visible button and detail panel. If the action is not a fresh `立即沟通`, skip it as already contacted or not actionable.
   - If every visible result on the current page/list is already contacted or unsuitable, scroll the job list to reveal more companies and continue scanning before declaring failure.

4. Complete the communication flow for one job.
   - Open the job detail.
   - Click the first visible `立即沟通`.
   - When a popup or confirmation dialog appears, click the second `立即沟通`.
   - If the flow opens the chat page, continue to messaging.
   - If the UI asks for login, captcha, QR scan, phone verification, resume selection with ambiguous choices, or any other unhandleable step, mark this job as failed and move to another result if possible.

5. Send exactly one HR message.
   - Generate a short, natural Chinese message based on both the user's instruction, if any, and the visible job/company/JD context.
   - Pull 1-3 grounded details from the JD, such as role direction, tech stack, testing type, large-model/AIGC tasks, automation, API testing, or business domain. If the JD is too sparse, use the job title and visible tags instead.
   - Keep it truthful and modest. Do not invent education, years of experience, project history, salary expectation, location status, availability, certificates, or technologies that the user did not provide and that are not visible in the conversation.
   - Click the chat input, type the message with `write`, then send it with `key press enter`. For Chinese text that does not enter correctly, set the clipboard from the shell and paste with `cli-anything-pyautogui hotkey ctrl v`, then press Enter.
   - Do not send follow-up messages unless the user explicitly asks in the same task.

6. Count completion.
   - One application is complete only after one tailored message has been sent in the chat page.
   - Add the company/job/recruiter to `completed`.
   - Return to the job search/list page for the next application by clicking the top `职位` navigation entry or using the browser back button/`cli-anything-pyautogui hotkey alt left`.
   - After returning, take a fresh screenshot before selecting the next job, because Boss may preserve scroll position or change button states.
   - Repeat until the target count is completed or no workable matching jobs remain.

## Message Writing Rules

Use one concise message. Adapt tone to the user's prompt. If the user gives no wording preference, use a professional, direct style:

```text
您好，我对贵公司的[岗位名]很感兴趣，看到岗位方向和[可见JD要点/用户给出的能力点]比较匹配。方便的话想进一步了解岗位要求和团队情况，谢谢。
```

When the user provides points to emphasize, combine those points with visible JD evidence:

- Example user instruction: `强调我会自动化测试和接口测试`
- Example message:
  `您好，我对贵公司的测试开发工程师岗位很感兴趣，看到岗位涉及自动化测试、接口测试和质量保障方向，和我想重点沟通的自动化/接口测试能力比较匹配。方便的话想进一步了解岗位要求和团队情况，谢谢。`

- Example user instruction: `投递 AI 大模型应用开发`
- Example message:
  `您好，我对贵公司的 AI 大模型应用开发岗位很感兴趣，看到岗位涉及大模型应用落地、AIGC/算法应用和工程开发，方向比较匹配。方便的话想进一步了解岗位要求和团队情况，谢谢。`

If job/company/JD text is not visible, avoid pretending it is known:

```text
您好，我对这个测试开发相关岗位很感兴趣，想进一步了解岗位要求和团队情况，谢谢。
```

## Failure Handling

Fully automate after the user requests a target role and count. Do not stop for normal click/search/chat decisions. Treat the following as failed attempts and continue when possible:

- Boss is not open or the UI is not inspectable.
- The account is logged out, requires QR scan, captcha, SMS, or phone verification.
- A popup requires choosing between multiple resumes or identities and the right choice is not obvious.
- `立即沟通` is missing, disabled, or replaced by a non-application action.
- The job appears previously contacted/applied, including visible `继续沟通`, `已沟通`, existing chat, or a completed record from the current run/conversation.
- The job is visibly unrelated to the target role.
- The chat input cannot be found or message sending cannot be verified.
- The page appears blocked by anti-bot, rate limiting, or a platform safety challenge.
- All visible jobs have already been contacted or are unsuitable and scrolling no longer reveals new companies.

Do not try to bypass captcha, verification, anti-bot systems, or platform restrictions. Do not spam repeated messages. Do not operate beyond the user's requested count.

## Reporting

At the end, report in Chinese:

- Completed count.
- Failed count, if any.
- Company and job title for each successful application when visible.
- Jobs skipped because they were already contacted, when visible.
- Failure reasons for skipped jobs or blocked steps.
- Any important uncertainty, such as a message that appeared typed but not visually confirmed as sent.

Keep the report compact. The user cares most about what was actually completed.

## Manual Eval Prompts

Use these prompts to test whether this skill leads to the intended behavior:

1. `Boss 已打开，帮我投递 2 个测试开发工程师岗位，话术偏简洁。`
2. `帮我在 Boss 搜 Java 测试开发，投递 1 家，强调我会自动化测试和接口测试。`
3. `Boss 页面卡住了，继续帮我完成 3 个软件测试相关岗位投递，失败的跳过。`
4. `继续帮我投递 2 个 AI 大模型应用开发岗位，不要投之前沟通过的公司，如果当前页都投过就往下滑。`
