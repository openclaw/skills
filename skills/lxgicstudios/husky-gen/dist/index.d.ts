export declare function analyzeProject(): Promise<string>;
export declare function generateHooks(pkgContent: string): Promise<{
    preCommit: string;
    prePush: string;
    commitMsg: string;
}>;
export declare function installHooks(hooks: {
    preCommit: string;
    prePush: string;
    commitMsg: string;
}): void;
