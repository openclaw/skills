export declare function getCommitsSinceLastTag(): Promise<string>;
export declare function getCurrentVersion(): Promise<string>;
export interface ReleaseInfo {
    version: string;
    bump: string;
    notes: string;
}
export declare function generateRelease(commits: string, currentVersion: string): Promise<ReleaseInfo>;
export declare function createTag(version: string, notes: string): Promise<void>;
