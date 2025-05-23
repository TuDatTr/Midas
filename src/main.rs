#![feature(downcast_unchecked)]
#![feature(let_chains)]
#![feature(unchecked_math)]
#![feature(trait_alias)]

extern crate core;

pub mod cache;
pub mod r#const;
pub mod evm;
pub mod executor;
pub mod feedback;
pub mod fuzzer;
pub mod fuzzers;
pub mod generic_vm;
pub mod indexed_corpus;
pub mod input;
pub mod minimizer;
pub mod mutation_utils;
pub mod oracle;
pub mod scheduler;
pub mod state;
pub mod state_input;
pub mod tracer;

use clap::Parser;
use clap::Subcommand;

use evm::{evm_main, EvmArgs};
use tracing::Level;
use tracing_subscriber::FmtSubscriber;

#[derive(Parser)]
#[command(author, version, about)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    EVM(EvmArgs),
}

fn main() {
    let subscriber_builder = FmtSubscriber::builder()
        .compact()
        .with_target(false)
        .without_time();
    #[cfg(debug_assertions)]
    let subscriber = subscriber_builder.with_max_level(Level::DEBUG).finish();
    #[cfg(not(debug_assertions))]
    let subscriber = subscriber_builder.with_max_level(Level::INFO).finish();

    tracing::subscriber::set_global_default(subscriber).expect("failed to initialize logger");

    let args = Cli::parse();
    match args.command {
        Commands::EVM(args) => {
            evm_main(args);
        }
    }
}
