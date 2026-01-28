import OpenAI from "openai";

const openai = new OpenAI();

export async function generate(description: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a Terraform expert. Generate complete, production-ready Terraform configuration from the description. Include: provider config, all resources with proper naming, variables.tf, outputs.tf, terraform.tfvars example, security groups, IAM roles where needed, tags, and a README with apply instructions. Follow Terraform best practices: modules, state management notes.` },
      { role: "user", content: description }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "";
}
