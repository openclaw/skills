export declare function generateSQL(query: string, options: {
    dialect?: string;
    schema?: string;
}): Promise<string>;
