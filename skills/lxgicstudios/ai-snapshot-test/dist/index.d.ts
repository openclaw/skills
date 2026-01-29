export declare function generateSnapshotTest(filePath: string): Promise<{
    testCode: string;
    testPath: string;
}>;
export declare function writeTestFile(path: string, code: string): void;
