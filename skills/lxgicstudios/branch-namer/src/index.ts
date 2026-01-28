import OpenAI from "openai";
import simpleGit from "simple-git";

const openai = new OpenAI();

export async function generateBranchName(description: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You generate git branch names from descriptions. Rules:
- Use conventional prefixes: feat/, fix/, chore/, refactor/, docs/, test/
- Use kebab-case after the prefix
- Keep it under 50 chars total
- Be descriptive but concise
- Return ONLY the branch name, nothing else`
      },
      { role: "user", content: description }
    ],
    temperature: 0.3,
  });

  return response.choices[0].message.content?.trim() || "feat/update";
}

export async function createAndCheckout(branchName: string): Promise<void> {
  const git = simpleGit();
  await git.checkoutLocalBranch(branchName);
}

export async function createBranch(description: string, checkout: boolean = false): Promise<string> {
  const branchName = await generateBranchName(description);
  if (checkout) {
    await createAndCheckout(branchName);
  }
  return branchName;
}
