from tools.agent_tools.skill.service import load_skill


def run_load_skill(args):
    """Load skill content by name."""
    return load_skill(args.get("name", ""))
