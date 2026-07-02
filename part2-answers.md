## Part 2: Git, GitHub, and Docker (just answer in your own words)

No code needed for this part. Short, clear answers are fine.

1. What's the difference between `git fetch` and `git pull`?
git fetch only downloads the latest updates from the remote server to see what changed, without modifying local files. git pull downloads the latest updates and immediately mixes them into the active working files.

2. Explain what a merge conflict is and how you'd fix one.
A conflict happen when two developers edit the exact same line of a file with different approach. To fix it, the developer opens the file, locates the conflict markers, manually deletes the unwanted version, and commits the clean file.

3. What's the difference between merge and rebase? When would you use each?
merge combines branches by adding a new "merge commit" at the end, keeping history intact. rebase moves the entire branch to the tip of main for a clean, straight-line history. rebase cleans up local commits before opening a PR, while merge integrates shared team features.

4. What's the difference between squash and fixup commits?
Both combine a chain of small commits into one. squash allows combining and editing the commit messages into a new summary, while fixup discards the newer messages and keeps only the original parent message.

5. What is trunk-based development? How is it different from using long-lived feature branches?
Trunk-based means developers merge small, frequent updates directly into main multiple times a day. Long-lived branches mean working in isolation for weeks, which usually causes painful merge conflicts later.

6. How do teams avoid breaking `main` when working directly on it or with short-lived branches?
By blocking direct force-pushes to main, requiring automated testing pipelines to pass on every pull request, enforcing peer code reviews, and using feature flags.

7. What's your ideal PR process, from creating a branch to merging it?
Creating a small branch, coding the feature with tests, opening a PR, letting the CI pipeline run checks, obtaining peer approval, and squash-merging back into main.

8. What's the difference between a Docker image and a container?
An image is a static, read-only blueprint packaging the application environment and dependencies. A container is the active, live running instance of that image.

9. Why do we care about layer caching in a Dockerfile?
Docker builds images sequentially from top to bottom. Putting heavy, rarely changed steps (like installing requirements.txt) at the top allows Docker to cache them and skip rebuilding them later, cutting build times from minutes to seconds.

10. Should your database run in the same container as your app, or a separate one? Why?
Separate containers. This ensures that if the app layer crashes or needs to scale up, the database stays safe and unaffected. It also prevents them from fighting for the same CPU and memory resources.

### CI/CD
11. What is CI/CD, in your own words?
CI (Continuous Integration) automatically builds and tests code every time it is pushed to catch bugs early. CD (Continuous Deployment) automatically deploys that passing code straight to live servers.

12. What would you put in a CI pipeline for this project? (think tests, linting, build steps)
1. Build: Set up a clean environment and run pip install -r requirements.txt.
2. Linting: Run a style check to catch formatting errors.
3. Test: Execute the pytest suite to verify endpoints and Pydantic models working properly.

13. What's the difference between continuous delivery and continuous deployment?
Continuous Delivery automatically tests and builds the code so it is release-ready, but waits for a human to click a button to go live. Continuous Deployment pushes the code live completely automatically the moment tests pass.

14. If a build fails in CI, what should happen to the PR? Should it be allowed to merge?
The PR must be automatically locked and blocked from merging. The developer must push a fix and wait for the entire automation pipeline to turn green first.

15. How would you handle secrets (like DB passwords or API keys) in a CI/CD pipeline?
Secrets are never hardcoded. They are stored securely as encrypted variables in the repository settings (like GitHub Actions Secrets) and injected into the pipeline dynamically at runtime.

---

## What We're Looking For
- Can you design a clean API and use Pydantic properly, not just make it "work"
- Do you understand git concepts, not just memorized commands
- Can you explain Docker basics clearly
- Can you communicate your reasoning simply
